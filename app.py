from flask import Flask, render_template, request, redirect, url_for, session, flash
app = Flask(__name__)

# Chave secreta:
app.secret_key = 'chaveSecreta5252'

# SIMULAÇÃO DE BANCO DE DADOS:

# Usuários cadastrados:
USUARIOS = {
    "funcionario@wayne.com": {"nome": "Lucius Fox", "senha": "123", "cargo": "Funcionario"},
    "gerente@wayne.com": {"nome": "Alfred Pennyworth", "senha": "123", "cargo": "Gerente"},
    "admin@wayne.com": {"nome": "Bruce Wayne", "senha": "123", "cargo": "Administrador"}
}

# Inventário:
RECURSOS = [
    {"id": 1, "nome": "Batmóvel", "tipo": "Veículo", "status": "Operacional"},
    {"id": 2, "nome": "Traje de Combate", "tipo": "Equipamento", "status": "Em Manutenção"},
    {"id": 3, "nome": "Drone de Vigilância", "tipo": "Segurança", "status": "Operacional"},
]

# Áreas das Indústrias Wayne
AREAS_RESTRITAS = [
    {"nome": "Refeitório e Escritórios", "nivel_minimo": "Funcionario"},
    {"nome": "Laboratório de Pesquisa", "nivel_minimo": "Gerente"},
    {"nome": "Batcaverna", "nivel_minimo": "Administrador"}
]

# Histórico de atividades recentes dos funcionários (Simulação de log do sistema)
ATIVIDADES_FUNCIONARIOS = [
    {"tempo": "Há 2 min", "nome": "Lucius Fox", "cargo": "Funcionario", "acao": "Acessou o Refeitório e Escritórios"},
    {"tempo": "Há 15 min", "nome": "Alfred Pennyworth", "cargo": "Gerente", "acao": "Atualizou status do Traje de Combate"},
    {"tempo": "Há 40 min", "nome": "Bruce Wayne", "cargo": "Administrador", "acao": "Entrou na Batcaverna"},
    {"tempo": "Há 1 hora", "nome": "Lucius Fox", "cargo": "Funcionario", "acao": "Cadastrou um novo dispositivo de Segurança"}
]

# AUTENTICAÇÃO:
@app.route('/')
def index():
    if 'usuario' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        user = USUARIOS.get(email)
        if user and user['senha'] == senha:
            session['usuario'] = user['nome']
            session['cargo'] = user['cargo']
            session['email'] = email
            flash(f"Bem-vindo de volta, {user['nome']}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Credenciais inválidas. Acesso negado.", "danger")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Sessão encerrada com segurança.", "info")
    return redirect(url_for('login'))

# DASHBOARD E GESTÃO DE RECURSOS DA EMPRESA WAYNE
@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        flash("Por favor, faça login primeiro.", "warning")
        return redirect(url_for('login'))
    
    # Renderiza o painel com os dados atuais
    return render_template(
        'dashboard.html', 
        usuario=session['usuario'], 
        cargo=session['cargo'],
        recursos=RECURSOS,
        areas=AREAS_RESTRITAS,
        atividades=ATIVIDADES_FUNCIONARIOS
    )

# Adicionar Recurso (Apenas Gerentes e Admins de Segurança)
@app.route('/recurso/adicionar', methods=['POST'])
def adicionar_recurso():
    if session.get('cargo') not in ['Gerente', 'Administrador']:
        return redirect(url_for('acesso_negado'))
        
    nome = request.form.get('nome')
    tipo = request.form.get('tipo')
    status = request.form.get('status')
    
    novo_id = max([r['id'] for r in RECURSOS]) + 1 if RECURSOS else 1
    RECURSOS.append({"id": int(novo_id), "nome": nome, "tipo": tipo, "status": status})
    flash(f"Recurso '{nome}' adicionado com sucesso!", "success")
    return redirect(url_for('dashboard'))

# Remover Recurso (Apenas Administradores de Segurança) com REORDENAÇÃO DE ID
@app.route('/recurso/remover/<int:recurso_id>')
def remover_recurso(recurso_id):
    if session.get('cargo') != 'Administrador':
        return redirect(url_for('acesso_negado'))
        
    global RECURSOS
    # Filtrando diretamente na variável global RECURSOS
    RECURSOS = [r for r in RECURSOS if r['id'] != recurso_id]
    
    # Reordena os IDs automaticamente (1, 2, 3...)
    for indice, recurso in enumerate(RECURSOS):
        recurso['id'] = indice + 1
        
    flash("Recurso removido e registros de ID reordenados com sucesso.", "success")
    return redirect(url_for('dashboard'))

# Atualizar Dados do Recurso (Nome, Tipo e Status) - Gerentes e Administradores
@app.route('/recurso/atualizar/<int:recurso_id>', methods=['POST'])
def atualizar_recurso(recurso_id):
    if session.get('cargo') not in ['Gerente', 'Administrador']:
        return redirect(url_for('acesso_negado'))
        
    # Obtém os novos valores enviados do formulário de edição
    novo_nome = request.form.get('nome')
    novo_tipo = request.form.get('tipo')
    novo_status = request.form.get('status')
    
    for r in RECURSOS:
        if r['id'] == recurso_id:
            r['nome'] = novo_nome
            r['tipo'] = novo_tipo
            r['status'] = novo_status
            flash(f"Recurso '{novo_nome}' atualizado com sucesso!", "success")
            break
            
    return redirect(url_for('dashboard'))

# CONTROLE DE ACESSO A ÁREAS
@app.route('/acesso_area/<string:nivel_area>')
def acessar_area(nivel_area):
    if 'usuario' not in session:
        return redirect(url_for('login'))
        
    hierarquia = {"Funcionario": 1, "Gerente": 2, "Administrador": 3}
    nivel_usuario = hierarquia.get(session.get('cargo'), 0)
    nivel_exigido = hierarquia.get(nivel_area, 4)
    
    if nivel_usuario >= nivel_exigido:
        flash("Acesso autorizado! Entrada liberada.", "success")
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('acesso_negado'))

@app.route('/acesso_negado')
def acesso_negado():
    return render_template('negado.html')

if __name__ == '__main__':
    app.run(debug=True)