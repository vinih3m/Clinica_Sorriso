import re
import sys
from pathlib import Path

if len(sys.argv) < 2:
    print("Use assim:")
    print("python limpar_css_exato_agenda.py caminho/do/agenda.html")
    sys.exit(1)

arquivo = Path(sys.argv[1])

if not arquivo.exists():
    print(f"Arquivo não encontrado: {arquivo}")
    sys.exit(1)

conteudo = arquivo.read_text(encoding="utf-8")

style_match = re.search(
    r"<style[^>]*>(.*?)</style>",
    conteudo,
    re.DOTALL | re.IGNORECASE
)

if not style_match:
    print("Nenhum bloco <style> encontrado.")
    sys.exit(1)

css = style_match.group(1)

padrao = re.compile(r"([^{}]+)\{([^{}]*)\}", re.DOTALL)

vistos = set()
novo_css_partes = []
ultimo_fim = 0
removidos = []

for match in padrao.finditer(css):
    seletor_original = match.group(1)
    propriedades_original = match.group(2)

    seletor_limpo = " ".join(seletor_original.strip().split())

    props_limpo = "\n".join(
        linha.strip()
        for linha in propriedades_original.strip().splitlines()
        if linha.strip()
    )

    # Evita mexer em @keyframes, @media e blocos especiais
    if (
        not seletor_limpo
        or seletor_limpo.startswith("@")
        or seletor_limpo in ["from", "to"]
        or seletor_limpo.endswith("%")
    ):
        novo_css_partes.append(css[ultimo_fim:match.end()])
        ultimo_fim = match.end()
        continue

    chave = (seletor_limpo, props_limpo)

    if chave in vistos:
        linha = css[:match.start()].count("\n") + 1
        removidos.append((linha, seletor_limpo))

        # mantém o texto entre o último fim e o início do bloco,
        # mas remove o bloco duplicado
        novo_css_partes.append(css[ultimo_fim:match.start()])
        ultimo_fim = match.end()
        continue

    vistos.add(chave)
    novo_css_partes.append(css[ultimo_fim:match.end()])
    ultimo_fim = match.end()

novo_css_partes.append(css[ultimo_fim:])
novo_css = "".join(novo_css_partes)

novo_conteudo = (
    conteudo[:style_match.start(1)]
    + novo_css
    + conteudo[style_match.end(1):]
)

saida = arquivo.with_name(arquivo.stem + "_css_limpo" + arquivo.suffix)

saida.write_text(novo_conteudo, encoding="utf-8")

print("\nArquivo limpo criado:")
print(saida)

print("\nBlocos CSS duplicados removidos:")
for linha, seletor in removidos:
    print(f"linha {linha}: {seletor}")

print(f"\nTotal removido: {len(removidos)} blocos")
print("\nIMPORTANTE: o arquivo original NÃO foi alterado.")