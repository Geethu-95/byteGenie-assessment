from flask import Flask, jsonify, request;
import csv
import json
from langchain.document_loaders import SeleniumURLLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.llms import CTransformers
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from urllib.parse import unquote
from langchain import OpenAI
import os
from flask_cors import CORS, cross_origin

os.environ["OPENAI_API_KEY"] = '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'

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

#1. Extract Data From the Website
def extract_data_website(url):
    loader=SeleniumURLLoader([url])
    data=loader.load()
    text=""
    for page in data:
        text +=page.page_content + " "
        return text


# 2. Generate a Summary of the Text
def split_text_chunks_and_summary_generator(textData):
    text_splitter = CharacterTextSplitter(separator='\n',
                                        chunk_size=1000,
                                        chunk_overlap=20)
    text_chunks = text_splitter.split_text(textData)
    print(len(text_chunks))

    # llm = CTransformers(model='models\llama-2-7b-chat.ggmlv3.q4_0.bin',
    #                    model_type='llama',
    #                    config={'max_new_tokens': 128,
    #                            'temperature': 0.01}
    #                    )
    llm = OpenAI()

    docs = [Document(page_content=t) for t in text_chunks]
    chain = load_summarize_chain(llm=llm, chain_type='map_reduce', verbose=True)
    summary = chain.run(docs)
    print(summary)
    return summary


@app.route('/', methods=['GET', 'POST'])
def home():
    return "Summary Generator"


@app.route('/summary_generate_partialDoc/<data>', methods=['GET', 'POST'])
@cross_origin()
def summary_generate_partialDoc(data):
    # textData = request.args.get('data')
    textData = data;
    if not textData:
        return jsonify({'error': 'text is required'}), 400
    print("Inisde func")
    summary = split_text_chunks_and_summary_generator(textData)
    print("Here is the Complete Summary", summary)
    response = {
        # 'submitted_url': encode_url,
        'summary': summary
    }
    return jsonify(response)

@app.route('/summary_generate/<data>', methods=['GET', 'POST'])
@cross_origin()
def summary_generate(data):
    # encode_url = unquote(unquote(request.args.get('url')))
    # encode_url = unquote(unquote(url));
    # encode_url = url;
    # print(encode_url)
    textData = data;
    if not textData:
        return jsonify({'error': 'Data is required'}), 400
    # textData = extract_data_website(data)
    summary = split_text_chunks_and_summary_generator(textData)
    print("Here is the Complete Summary", summary)
    response = {
        # 'submitted_url': encode_url,
        'summary': summary
    }
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
