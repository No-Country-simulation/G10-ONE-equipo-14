FROM python:3.12-slim
WORKDIR /dashboard
COPY dashboard/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY dashboard/app.py dashboard/api_client.py dashboard/service_status.py ./
COPY dashboard/assets ./assets
COPY dashboard/.streamlit ./.streamlit
CMD ["sh", "-c", "exec streamlit run app.py --server.address=0.0.0.0 --server.port=${PORT:-8501}"]
