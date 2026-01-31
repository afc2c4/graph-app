from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import db

@asynccontextmanager
async def lifespan(app: FastAPI):
    db.connect()
    yield
    db.close()

app = FastAPI(lifespan=lifespan)

# Permite que o Frontend acesse o Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware simples para logar requisições (útil em dev)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    client = request.client.host if request.client else "unknown"
    print(f"{client} {request.method} {request.url} UA={request.headers.get('user-agent')}")
    response = await call_next(request)
    return response

# Rota raiz para evitar 404 em requisições diretas à raiz
@app.get("/")
def root():
    return {"status": "ok", "service": "graph-app"}

@app.post("/seed")
def seed_cloud_db():
    # Cria nós e relacionamentos no banco na nuvem
    query = """
    MATCH (n) DETACH DELETE n 
    WITH 1 as dummy
    CREATE (ana:Person {name: 'Ana', role: 'Dev'})
    CREATE (beto:Person {name: 'Beto', role: 'Product'})
    CREATE (carlos:Person {name: 'Carlos', role: 'Design'})
    CREATE (dani:Person {name: 'Dani', role: 'Tech Lead'})
    
    CREATE (ana)-[:AMIGO_DE]->(beto)
    CREATE (beto)-[:AMIGO_DE]->(carlos)
    CREATE (carlos)-[:AMIGO_DE]->(dani)
    CREATE (dani)-[:AMIGO_DE]->(ana)
    CREATE (ana)-[:AMIGO_DE]->(carlos)
    """
    # Usa uma transação de escrita com execute_write para garantir que o comando rode no modo de escrita
    with db.get_session() as session:
        def _seed(tx):
            tx.run(query)
        session.execute_write(_seed)
    # Verifica e retorna contagens para confirmar a operação
    with db.get_session() as session:
        nodes_count = session.run("MATCH (n) RETURN count(n) as c").single()["c"]
        rels_count = session.run("MATCH ()-[r]->() RETURN count(r) as c").single()["c"]
    return {"message": "Grafo Cloud Populado!", "nodes": nodes_count, "relationships": rels_count}

@app.get("/debug")
def debug_counts():
    """Retorna contagens simples para depuração (nós e relacionamentos)."""
    with db.get_session() as session:
        nodes_count = session.run("MATCH (n) RETURN count(n) as c").single()["c"]
        rels_count = session.run("MATCH ()-[r]->() RETURN count(r) as c").single()["c"]
    return {"nodes": nodes_count, "relationships": rels_count}

@app.get("/graph-data")
def get_graph():
    # Retorna a estrutura visual (Nós e Arestas)
    query = "MATCH (n)-[r]->(m) RETURN n, r, m"
    nodes = []
    links = []
    with db.get_session() as session:
        result = session.run(query)
        for record in result:
            n, m = record["n"], record["m"]
            nodes.append({"id": n.element_id, "name": n.get("name"), "group": "person"})
            nodes.append({"id": m.element_id, "name": m.get("name"), "group": "person"})
            links.append({"source": n.element_id, "target": m.element_id})
    
    # Remove duplicatas para o visualizador
    unique_nodes = list({v['id']:v for v in nodes}.values())
    return {"nodes": unique_nodes, "links": links}

@app.get("/analytics")
def get_analytics():
    # Calcula Centralidade (Influência) [cite: 45]
    query = """
    MATCH (p:Person)<-[:AMIGO_DE]-(f)
    RETURN p.name as name, count(f) as followers
    ORDER BY followers DESC
    """
    with db.get_session() as session:
        result = session.run(query)
        return [{"name": r["name"], "followers": r["followers"]} for r in result]