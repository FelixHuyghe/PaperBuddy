import json
from sqlalchemy import create_engine, Column, Integer, String, Text, ARRAY
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
import datasets
from tqdm import tqdm
import torch
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModel
from sqlalchemy.sql import select, func

Base = declarative_base()


class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    authors = Column(String, nullable=False)
    full_text = Column(Text, nullable=False)
    embedding = Column(
        Vector(384), nullable=False
    )  # Adjust the size of the vector as needed


DATABASE_URL = "postgresql://neondb_owner:XMSJfK0rhV4Z@ep-jolly-darkness-a20jze4h.eu-central-1.aws.neon.tech/neondb?options=endpoint%3Dep-jolly-darkness-a20jze4h"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

# Base.metadata.create_all(bind=engine)


def insert_paper(new_paper: Paper):
    session.add(new_paper)
    session.commit()


def insert_json(nbr):
    # Get embeddings
    embeddings = []
    json_file = f"neural_embeddings_{nbr}.json"
    with open(json_file, "r") as file:
        cur_embeddings = json.load(file)
        # Make sure the embeddings are flattened, and a 2D array is returned
        cur_embeddings = [item for sublist in cur_embeddings for item in sublist]
        embeddings.extend(cur_embeddings)

    print(len(embeddings))

    # if prefix == "averaged":
    # return np.array(embeddings).transpose().tolist
    start = 0
    for i, e in tqdm(enumerate(embeddings)):
        id = start + i
        new_paper = Paper()
        new_paper.embedding = e
        new_paper.title = (
            full_nlp_dataset[id]["title"] if full_nlp_dataset[id].get("title") else ""
        )
        new_paper.authors = (
            full_nlp_dataset[id]["authors"]
            if full_nlp_dataset[id].get("authors")
            else ""
        )
        new_paper.full_text = (
            full_nlp_dataset[id]["full_text"]
            if full_nlp_dataset[id].get("full_text")
            else ""
        )
        insert_paper(new_paper)


def get_latent_vector(to_embed):
    tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-small-en-v1.5")
    model = AutoModel.from_pretrained("BAAI/bge-small-en-v1.5")
    model.eval()
    encoded_input = tokenizer(
        to_embed, return_tensors="pt", padding=True, truncation=True
    )
    with torch.no_grad():
        model_output = model(**encoded_input)
        sentence_embeddings = model_output[0][:, 0]
    sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)
    return sentence_embeddings.numpy().tolist()


def get_nn(query, k):
    reference_vector = get_latent_vector(query)[0]

    # db_query = f"SELECT full_text FROM papers ORDER BY embedding <-> {reference_vector} LIMIT 5;"

    result = (
        session.query(
            Paper,
            Paper.embedding.cosine_distance(reference_vector),
        )
        .order_by(Paper.embedding.cosine_distance(reference_vector))
        .limit(k)
    )

    inters = []
    print("")
    for row in result:
        print("-" * 50 + "\n")
        print(row[0].title)
        print("\n" + "-" * 50)
        inters.append(
            "Title: "
            + row[0].title
            + "\n"
            + "Authors: "
            + row[0].authors
            + "\n"
            + "Full text: "
            + row[0].full_text
        )

    print(result)
    concat = ""
    for i in inters:
        concat += i + "\n\n"

    return concat


if __name__ == "__main__":
    get_nn("machine learning")
