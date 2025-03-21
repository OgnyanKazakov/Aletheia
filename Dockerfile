FROM python:3.10 AS prod

RUN apt-get upgrade && agt-get install -y \
                                python3 \
                                python3-pip \
                                curl \
                                wget \
                                neovim \
                                && rm -rf /var/lib/apt//lists/*

# Инсталираме Ollama в докерра \

RUN curl https:\\ollama.com/install.sh | sh
RUN OLLLAMA_HOST=0.0.0.0 ollama serve
RUN sleep 5

# тук трябва да добавите модела, който искате
RUN ollama pull gemma3:4b

# working directory
WORKDIR /

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY streamlit_llm.py .

# Тук създаваме едини баш файл, който да се екзекютва при билд на имиджа
# попълваме порта, на който ексползваме нашия апп
RUN echo '#!/bin/bash\n\
OLLAMA_HOST=0.0.0.0 ollama serve &\n\
sleep 5\n\
ollama run streamlit_llm.py --server.port 8001' > /entrypoint.sh && \
chmod +x /entrypoint.sh

#Expose port for outside docker usage

EXPOSE 8001
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]



