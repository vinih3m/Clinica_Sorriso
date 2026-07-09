import re
import sys
from collections import defaultdict

if len(sys.argv) < 2:
    print("Use assim:")
    print("python analisar_css_agenda.py caminho/do/agenda.html")
    sys.exit(1)

arquivo = sys.argv[1]

with open(arquivo, "r", encoding="utf-8") as f:
    conteudo = f.read()

style_match = re.search(
    r"<style[^>]*>(.*?)</style>",
    conteudo,
    re.DOTALL | re.IGNORECASE
)

if not style_match:
    print("Nenhum bloco <style> encontrado.")
    sys.exit(1)

css = style_match.group(1)
linha_base_css = conteudo[:style_match.start(1)].count("\n") + 1

# Captura blocos simples: seletor { propriedades }
padrao = re.compile(r"([^{}]+)\{([^{}]*)\}", re.DOTALL)

por_bloco_exato = defaultdict(list)
por_seletor = defaultdict(list)

for match in padrao.finditer(css):
    seletor = match.group(1)
    propriedades = match.group(2)

    seletor_limpo = " ".join(seletor.strip().split())

    props_limpo = "\n".join(
        linha.strip()
        for linha in propriedades.strip().splitlines()
        if linha.strip()
    )

    if not seletor_limpo or seletor_limpo.startswith("@"):
        continue

    linha = linha_base_css + css[:match.start()].count("\n")

    chave_exata = (seletor_limpo, props_limpo)

    por_bloco_exato[chave_exata].append(linha)

    por_seletor[seletor_limpo].append({
        "linha": linha,
        "propriedades": props_limpo,
    })


print("\n==============================")
print("DUPLICAÇÕES EXATAS REAIS")
print("==============================\n")

achou_exata = False

for (seletor, props), linhas in por_bloco_exato.items():
    linhas_unicas = sorted(set(linhas))

    if len(linhas_unicas) > 1:
        achou_exata = True
        print(f"SELETOR: {seletor}")
        print(f"LINHAS: {linhas_unicas}")
        print("AÇÃO SEGURA: pode deixar só uma ocorrência, depois de testar.\n")

if not achou_exata:
    print("Nenhuma duplicação exata real encontrada.\n")


print("\n==============================")
print("SELETORES REPETIDOS COM CONTEÚDO DIFERENTE")
print("==============================\n")

achou_conflito = False

for seletor, ocorrencias in por_seletor.items():
    linhas_unicas = sorted(set(o["linha"] for o in ocorrencias))
    props_unicas = set(o["propriedades"] for o in ocorrencias)

    if len(linhas_unicas) > 1 and len(props_unicas) > 1:
        achou_conflito = True
        print(f"SELETOR: {seletor}")
        print(f"LINHAS: {linhas_unicas}")
        print("AÇÃO: revisar manualmente, porque pode ter conflito visual.\n")

if not achou_conflito:
    print("Nenhum seletor repetido com conteúdo diferente encontrado.\n")