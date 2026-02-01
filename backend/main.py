from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import db

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n🚀 Iniciando aplicação...")
    db.connect()
    print("   → Populando banco com dados iniciais...")
    try:
        # Executa seed automático
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
        session = db.get_session()
        print(f"   DEBUG: Session criada - {session}")
        def _seed(tx):
            result = tx.run(query)
            return result
        
        result = session.execute_write(_seed)
        print(f"   DEBUG: Seed executado com sucesso")
        
        # Verifica se os dados foram criados
        check_result = session.run("MATCH (n) RETURN count(n) as c")
        count = check_result.single()["c"]
        print(f"   ✅ Seed carregado com sucesso! {count} nós criados")
        session.close()
    except Exception as e:
        print(f"   ❌ ERRO ao fazer seed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    yield
    db.close()
    print("🛑 Aplicação encerrada")

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
    import time
    client = request.client.host if request.client else "unknown"
    start_time = time.time()
    print(f"\n🔵 [REQUEST] {client} | {request.method} {request.url.path}")
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        print(f"✅ [RESPONSE] {response.status_code} | Time: {process_time:.3f}s")
        return response
    except Exception as e:
        print(f"❌ [ERROR] {str(e)}")
        raise

# Rota raiz para evitar 404 em requisições diretas à raiz
@app.get("/")
def root():
    return {"status": "ok", "service": "graph-app"}

@app.get("/status")
def status():
    """Retorna o status da conexão e dos dados no banco."""
    print("   → Verificando status do banco...")
    try:
        session = db.get_session()
        nodes_result = session.run("MATCH (n) RETURN count(n) as c")
        nodes_count = nodes_result.single()["c"]
        
        rels_result = session.run("MATCH ()-[r]->() RETURN count(r) as c")
        rels_count = rels_result.single()["c"]
        
        session.close()
        
        status_data = {
            "connected": True,
            "nodes": nodes_count,
            "relationships": rels_count,
            "database": "neo4j"
        }
        print(f"   ✅ Status: {status_data}")
        return status_data
    except Exception as e:
        print(f"   ❌ Erro ao verificar status: {e}")
        return {"connected": False, "error": str(e)}

@app.post("/seed")
def seed_cloud_db():
    print("   → Reiniciando seed do banco de dados...")
    try:
        session = db.get_session()
        
        # 1. Deleta todos os nós
        print("   → Deletando nós antigos...")
        delete_query = "MATCH (n) DETACH DELETE n"
        session.run(delete_query)
        print("   ✓ Nós deletados")
        
        # 2. Cria os novos nós
        print("   → Criando novos nós...")
        create_people = [
            ("CREATE (ana:Person {name: 'Ana', role: 'Dev'})", {}),
            ("CREATE (beto:Person {name: 'Beto', role: 'Product'})", {}),
            ("CREATE (carlos:Person {name: 'Carlos', role: 'Design'})", {}),
            ("CREATE (dani:Person {name: 'Dani', role: 'Tech Lead'})", {}),
        ]
        for q, params in create_people:
            session.run(q, params)
        print("   ✓ Nós criados")
        
        # 3. Cria os relacionamentos
        print("   → Criando relacionamentos...")
        relationships = [
            "MATCH (a:Person {name: 'Ana'}), (b:Person {name: 'Beto'}) CREATE (a)-[:AMIGO_DE]->(b)",
            "MATCH (a:Person {name: 'Beto'}), (b:Person {name: 'Carlos'}) CREATE (a)-[:AMIGO_DE]->(b)",
            "MATCH (a:Person {name: 'Carlos'}), (b:Person {name: 'Dani'}) CREATE (a)-[:AMIGO_DE]->(b)",
            "MATCH (a:Person {name: 'Dani'}), (b:Person {name: 'Ana'}) CREATE (a)-[:AMIGO_DE]->(b)",
            "MATCH (a:Person {name: 'Ana'}), (b:Person {name: 'Carlos'}) CREATE (a)-[:AMIGO_DE]->(b)",
        ]
        for rel_query in relationships:
            session.run(rel_query)
        print("   ✓ Relacionamentos criados")
        
        # 4. Verifica contagens
        print("   → Verificando contagens...")
        nodes_result = session.run("MATCH (n) RETURN count(n) as c").single()
        nodes_count = nodes_result["c"]
        
        rels_result = session.run("MATCH ()-[r]->() RETURN count(r) as c").single()
        rels_count = rels_result["c"]
        
        session.close()
        print(f"   ✅ Seed concluído: {nodes_count} nós, {rels_count} relacionamentos")
        return {"message": "Grafo Cloud Populado!", "nodes": nodes_count, "relationships": rels_count}
    except Exception as e:
        print(f"   ❌ Erro ao fazer seed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@app.get("/debug")
def debug_counts():
    """Retorna contagens simples para depuração (nós e relacionamentos)."""
    print("   → Consultando contagens...")
    try:
        session = db.get_session()
        nodes_count = session.run("MATCH (n) RETURN count(n) as c").single()["c"]
        rels_count = session.run("MATCH ()-[r]->() RETURN count(r) as c").single()["c"]
        session.close()
        print(f"   ✅ {nodes_count} nós, {rels_count} relacionamentos")
        return {"nodes": nodes_count, "relationships": rels_count}
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        raise

@app.get("/graph-data")
def get_graph():
    print("   → Recuperando dados do grafo...")
    query = "MATCH (n)-[r]->(m) RETURN n, r, m"
    nodes = []
    links = []
    try:
        session = db.get_session()
        result = session.run(query)
        for record in result:
            n, m = record["n"], record["m"]
            nodes.append({"id": n.element_id, "name": n.get("name"), "group": "person"})
            nodes.append({"id": m.element_id, "name": m.get("name"), "group": "person"})
            links.append({"source": n.element_id, "target": m.element_id})
        session.close()
        unique_nodes = list({v['id']:v for v in nodes}.values())
        print(f"   ✅ {len(unique_nodes)} nós, {len(links)} arestas")
        return {"nodes": unique_nodes, "links": links}
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        raise

@app.get("/analytics")
def get_analytics():
    print("   → Calculando centralidade...")
    query = """
    MATCH (p:Person)<-[:AMIGO_DE]-(f)
    RETURN p.name as name, count(f) as followers
    ORDER BY followers DESC
    """
    try:
        session = db.get_session()
        result = session.run(query)
        analytics = [{"name": r["name"], "followers": r["followers"]} for r in result]
        session.close()
        print(f"   ✅ {len(analytics)} pessoas com influência")
        return analytics
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        raise