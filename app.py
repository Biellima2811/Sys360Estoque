from flask import Flask, render_template, request, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = "chave_secreta_portfolio" # Necessário para mensagens flash

# Rota da Página Inicial
@app.route("/")
def index():
    return render_template("index.html")

# Rota para "Simular" Download
@app.route("/download")
def download():
    # Aqui você poderia servir o arquivo .exe real
    return "Obrigado por baixar o Sys360! O download iniciará em instantes."

# Rota de Contato (Simples)
@app.route("/contato", methods=["POST"])
def contato():
    nome = request.form.get("nome")
    email = request.form.get("email")
    # Aqui entraria a lógica para te enviar um e-mail
    print(f"Novo lead: {nome} - {email}")
    flash("Obrigado! Entraremos em contato.")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)