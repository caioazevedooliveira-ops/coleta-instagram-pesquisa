# Cole isto na sua IA

Abra o agente de IA (Claude Code, Codex, Gemini CLI ou similar) **dentro da pasta do projeto** e cole o bloco abaixo inteiro.

```
Você vai me ajudar a montar uma base de posts públicos do Instagram para uma pesquisa acadêmica, seguindo o método deste repositório. Antes de qualquer ação, leia README.md, PASSO_A_PASSO.md, modelos/REGRAS_PARA_A_IA.md e docs/etica_e_limites.md.

Regras que valem o tempo todo:
1. Nunca apague nem sobrescreva nada. Coleta nova vai para pasta nova com data e hora.
2. A pasta dados_brutos/ é só leitura. Você nunca edita um .ndjson.
3. Antes de rodar qualquer script ou comando, me mostre o comando e espere meu ok.
4. Não curta, não siga, não comente, não envie mensagem em nenhuma conta. Só leitura.
5. Se aparecer pedido de login, captcha, "aguarde alguns minutos" ou qualquer bloqueio: pare, me avise e não tente contornar.
6. Não invente número, data ou fonte. Se não tiver certeza, escreva "[não verificado]".
7. Uma pergunta por vez. Respostas curtas.
8. Ao terminar cada passo, diga em uma linha o que foi feito e o que falta.

O que fazer, nesta ordem:
A. Pergunte quais perfis vou coletar, o período (início e fim) e o fuso. Monte o perfis.csv a partir de modelos/perfis.csv e me mostre antes de salvar.
B. Crie as pastas do passo 2 do PASSO_A_PASSO.md e copie modelos/REGRAS_PARA_A_IA.md para a raiz como CLAUDE.md ou AGENTS.md, conforme o agente que você é.
C. Me guie pelo passo 1 (instalação), um item por vez, e confirme comigo o teste do contador do Zeeschuimer.
D. Para cada perfil: rode scripts/rolar_firefox.py no feed e em /reels, depois me peça para baixar o .ndjson, mover para dados_brutos/ e clicar em Delete no Zeeschuimer. Se eu estiver em Windows ou Linux, me diga como rolar à mão.
E. Rode scripts/importar_ndjson.py e me mostre o resumo.txt. Se algum grupo não chegou no início do período, volte ao passo D para esse perfil.
F. Rode scripts/verificar_base.py para cada grupo. Me mostre repetidos, vazios e dias sem post.
G. Para cada dia sem post, siga o passo 7 do PASSO_A_PASSO.md e registre a classificação em documentos/dias_sem_post.csv.
H. Se eu pedir vídeos e transcrição: siga o passo 10 do PASSO_A_PASSO.md (baixar_midia.py, transcrever.py). Antes de instalar faster-whisper ou openpyxl, me mostre origem, o que faz e peça ok. Avise que vídeo só com música sai vazio. Depois gere a planilha com scripts/gerar_planilha.py (arquivo novo, nunca sobre a anterior).
I. Ao final, escreva documentos/relatorio_<data>.md com: o que foi coletado (perfis, período, total de posts por grupo), o que falta, e as lacunas declaradas.

Comece pelo item A.
```

## Se você usa duas IAs

Dá para separar os papéis: uma IA **coordena** (planeja, escreve o pedido, confere o resultado) e outra **executa** (roda os scripts e devolve um relatório curto). Quem confere não deve ser quem executou. Veja o modelo de pedido em `modelos/REGRAS_PARA_A_IA.md`, seção "Delegar".
