# Passo a passo

Siga na ordem. Cada passo tem **o que fazer** e **como saber que deu certo**. Os passos 1 a 3 são feitos uma vez; os passos 4 a 7 se repetem a cada coleta; os passos 8 a 11 completam a base.

Os comandos abaixo rodam no Terminal, sempre **de dentro da pasta do projeto**.

---

## 1. Preparar o computador (uma vez)

**O que fazer**
1. Instale o [Firefox](https://www.mozilla.org/firefox/).
2. Abra a página de *releases* do [Zeeschuimer](https://github.com/digitalmethodsinitiative/zeeschuimer/releases), baixe o arquivo `.xpi` mais recente e abra-o no Firefox. Aceite a instalação.
3. Clique no ícone **Z** na barra do Firefox e ligue a chave do **Instagram**.
4. Crie uma conta nova no Instagram só para a pesquisa e entre nela no Firefox. Não use a sua conta pessoal.
5. Só no Mac: vá em Ajustes > Privacidade e Segurança > Acessibilidade e ligue o **Terminal** (ou o app de onde vai rodar os scripts). Sem isso o script não consegue apertar Page Down. Só no Linux: instale o `xdotool` (`sudo apt install xdotool`). No Windows não precisa de nada.
6. Confira o Python: `python3 --version`. Precisa ser 3.9 ou mais novo.

**Como saber que deu certo**
Abra qualquer perfil público no Firefox, role um pouco e clique no **Z**: o contador de itens do Instagram deve subir.

---

## 2. Montar a pasta do projeto (uma vez)

**O que fazer**
1. Baixe este repositório (botão *Code > Download ZIP* ou `git clone`) e renomeie a pasta com o nome do seu projeto.
2. Dentro dela, crie as pastas `dados_brutos/`, `saida/` e `documentos/`.
3. Copie `modelos/REGRAS_PARA_A_IA.md` para a raiz com o nome `CLAUDE.md` (Claude Code) ou `AGENTS.md` (Codex e outros). Se usar os dois, copie duas vezes.
4. Copie `modelos/perfis.csv` para a raiz e preencha: uma linha por perfil, com o **grupo** (ex.: `candidata_a`), o **perfil** (o @ sem o arroba) e, se houver, os **aliases** (outro @ da mesma conta, separados por `;`).

A pasta fica assim:

```
meu_projeto/
├── CLAUDE.md  (ou AGENTS.md)
├── perfis.csv
├── scripts/
├── dados_brutos/      ← .ndjson do Zeeschuimer. Só leitura. Nunca edite.
├── saida/             ← CSVs gerados. Uma pasta nova por coleta.
└── documentos/        ← relatórios, decisões, roteiro
```

**Como saber que deu certo**
`python3 scripts/importar_ndjson.py --help` mostra a ajuda sem erro.

---

## 3. Decidir o período e registrar (uma vez)

**O que fazer**
Escreva em `documentos/decisoes.md`: data de início, data de fim, fuso horário, lista de perfis e o motivo de cada escolha. Isso vai para o texto final da pesquisa.

**Como saber que deu certo**
Você consegue responder "de quando a quando, de quem e por quê" sem olhar outra coisa.

---

## 4. Rolar o perfil (a cada coleta)

**O que fazer**
1. Deixe o Firefox aberto, com a conta de pesquisa logada e a chave do Instagram ligada no Z.
2. No Terminal, rode para o feed:
   ```
   python3 scripts/rolar_firefox.py nome_do_perfil --rolagens 40
   ```
3. Depois rode para a aba de vídeos (é dela que vêm as reproduções):
   ```
   python3 scripts/rolar_firefox.py nome_do_perfil/reels --rolagens 40
   ```
4. Não mexa no computador enquanto roda. O script espera de 3 a 7 segundos entre uma rolagem e outra, ritmo de pessoa lendo. No Mac, se outro app vier para a frente, ele para sozinho; no Windows e no Linux ele não percebe isso, então deixe o Firefox na frente até acabar.

Quantas rolagens? 30 a 40 cobrem algumas semanas de um perfil ativo. Se no passo 6 o importador avisar que o post mais antigo ainda é depois do início do período, volte aqui e role mais (60, 100, 200).

**Sem script:** abra o perfil, clique na página e aperte Page Down a cada 3 a 7 segundos, 30 a 40 vezes. Faça o mesmo em `instagram.com/nome_do_perfil/reels/`.

**Como saber que deu certo**
O contador do Z subiu. Em geral, cada rolagem traz uns 12 posts.

---

## 5. Baixar o arquivo bruto e guardar (a cada coleta)

**O que fazer**
1. Clique no **Z**, na linha do Instagram clique em **Download** e escolha o formato **ndjson**.
2. Mova o arquivo baixado para `dados_brutos/`. Não renomeie, não abra para editar.
3. Ainda no Z, clique em **Delete** para zerar o contador antes do próximo perfil. Sem isso, o próximo download repete tudo o que já foi baixado (não é erro, o importador remove repetidos, mas os arquivos ficam enormes).
4. Repita os passos 4 e 5 para cada perfil.

**Como saber que deu certo**
Há um arquivo `zeeschuimer-export-instagram.com-<data>.ndjson` em `dados_brutos/` para cada perfil e aba rolados.

---

## 6. Transformar em planilha (a cada coleta)

**O que fazer**
```
python3 scripts/importar_ndjson.py dados_brutos/*.ndjson --perfis perfis.csv --inicio 2026-01-01 --fim 2026-03-31
```
Troque as datas pelo seu período. O script cria `saida/coleta_<data>_<hora>/` com um `posts_<grupo>.csv` por grupo e um `resumo.txt`.

Ele nunca escreve por cima de uma coleta anterior: cada rodada é uma pasta nova. Quando o mesmo post aparece no feed e na aba Reels, as duas versões são juntadas para preencher as reproduções.

**Como saber que deu certo**
O `resumo.txt` mostra, por grupo, quantos posts entraram e de que data a que data. Se disser "ainda não chegou no início do período", volte ao passo 4 e role mais fundo.

---

## 7. Verificar e procurar lacunas (a cada coleta)

**O que fazer**
```
python3 scripts/verificar_base.py saida/coleta_<data>_<hora>/posts_<grupo>.csv --inicio 2026-01-01 --fim 2026-03-31
```
Para comparar com a coleta anterior, acrescente `--anterior saida/coleta_<anterior>/posts_<grupo>.csv`.

O script lista: linhas e shortcodes repetidos, posts fora do período, curtidas e comentários vazios, vídeos sem reproduções e **os dias sem post**.

Para cada dia sem post:
1. Veja se há post no dia anterior ou seguinte perto da meia-noite (pode ser diferença de fuso).
2. Role de novo o feed e a aba Reels até passar daquele dia.
3. Classifique em `documentos/dias_sem_post.csv`: `tem_post_fora_da_base`, `fuso_diferente`, `sem_post` ou `nao_concluido`.

Rolar várias vezes e não achar nada é um **indício** de que não houve post, não uma prova. Escreva assim no texto.

**Como saber que deu certo**
Nenhum repetido, nenhum post fora do período, e cada dia sem post tem uma classificação.

---

## 8. Seguidores (todo dia, enquanto durar a coleta)

A extensão não traz seguidores. Abra o perfil no Firefox, passe o mouse sobre "seguidores" para ver o número exato e anote:

```
python3 scripts/anotar_seguidores.py nome_do_perfil=1234567 outro_perfil=98765
```

Isso acrescenta uma linha em `dados_brutos/seguidores.csv`. Se esquecer um dia, deixe o dia vazio; não invente nem interpole sem dizer.

---

## 9. Fechar a base

Quando a última coleta estiver verificada:
1. Some as linhas de todos os `posts_<grupo>.csv` da última pasta e anote o total em `documentos/decisoes.md`.
2. Liste as lacunas que ficaram (reproduções ausentes, curtidas ocultas, dias sem post não concluídos, seguidores sem registro). Elas vão para o texto da pesquisa.
3. Guarde `dados_brutos/` e `saida/` em um lugar seguro (nuvem do grupo). Não suba para o GitHub: o `.gitignore` já bloqueia.

---

## 10. Mídia, transcrição e planilha final (opcional)

**O que fazer**
1. Baixe os vídeos logo depois de capturar (os links expiram):
   ```
   python3 scripts/baixar_midia.py dados_brutos/*.ndjson --perfis perfis.csv --inicio 2026-01-01 --fim 2026-03-31 --so-videos
   ```
   Grava `midia/<grupo>/<data_hora>_<shortcode>.mp4` e um registro em `midia/registro_download.csv`.
2. Transcreva (roda no seu computador, sem custo; o primeiro uso baixa um modelo de uns 500 MB). Instale uma vez: `pip install faster-whisper`.
   ```
   python3 scripts/transcrever.py midia/<grupo> --idioma pt --saida saida/transcricoes_<grupo>.csv
   ```
   Pode parar e retomar: só transcreve o que ainda não está no CSV. Vídeo só com música ou sem áudio sai com texto vazio; o script não separa o motivo. Ouça 10 vídeos e compare com o texto antes de analisar.
3. Gere a planilha. Instale uma vez: `pip install openpyxl`.
   ```
   python3 scripts/gerar_planilha.py saida/coleta_<data>_<hora> --inicio 2026-01-01 --fim 2026-03-31 --transcricoes saida/transcricoes_<grupo>.csv
   ```
   Cria `saida/planilha_<data>_<hora>.xlsx` com as abas `leia_me` (dicionário), `resumo` (média e mediana), uma aba por grupo, `transcricoes` e `dias_sem_post`.

**Como saber que deu certo**
A planilha abre, a soma dos posts das abas bate com o `resumo.txt`, e as transcrições têm o mesmo número de vídeos baixados (menos os vazios, que você conta e declara).

Planilha nova a cada geração: nunca regrave sobre a anterior. Prefira a **mediana** à média, porque poucos posts virais puxam a média para cima.

---

## 11. Coletas seguintes (recoleta)

Para atualizar a base depois (outra semana, outro mês):
1. Repita os passos 4 a 7. Cada importação cria uma pasta nova em `saida/`.
2. Compare com a anterior: `verificar_base.py ... --anterior saida/coleta_<anterior>/posts_<grupo>.csv`. Ele mostra posts novos, posts que sumiram e reproduções recuperadas.
3. Métricas mudam com o tempo (curtidas sobem). Por isso guarde cada coleta com a sua data e hora, sem substituir a antiga, e diga no texto de qual coleta vem cada número.

---

## Se der problema

| Sintoma | O que fazer |
|---|---|
| "O Mac não deixou controlar o teclado" | Passo 1, item 5. Feche e abra o Terminal depois de ligar a permissão. |
| O Firefox pede login de novo, mostra captcha ou "aguarde alguns minutos" | Pare por hoje. Não insista e não troque de conta. Amanhã teste com poucas rolagens. |
| O importador diz "0 posts" | Confira o `perfis.csv`: o @ tem que ser igual ao da URL do perfil, sem o arroba. |
| Vídeos sem reproduções mesmo depois da aba Reels | Vídeos de contas parceiras (colaborações) não aparecem na aba Reels do perfil. Declare como lacuna. |
| O mesmo arquivo baixado duas vezes | Compare com `shasum -a 256 arquivo1 arquivo2`. Só se forem idênticos, mova um deles para uma pasta `duplicados/`. Nunca apague. |
