# Dicionário das colunas de `posts_<grupo>.csv`

| Coluna | O que é | De onde vem |
|---|---|---|
| `grupo` | Nome do grupo definido em `perfis.csv` (ex.: uma candidatura com conta oficial e conta de campanha) | `perfis.csv` |
| `perfil_da_captura` | O @ da página que estava aberta quando o post foi capturado | URL da página |
| `autor` | O @ que assina o post (pode diferir da captura em colaborações) | `data.user.username` |
| `shortcode` | Código único do post, o mesmo da URL `instagram.com/p/<shortcode>/` | `data.code` |
| `url` | Link do post | montado a partir do shortcode |
| `data_post` | Data e hora da publicação, no fuso escolhido | `data.taken_at` |
| `formato` | `imagem`, `carrossel`, `video` ou `reels` | `data.media_type` e `data.product_type` |
| `n_midias` | Quantas fotos ou vídeos o post tem (1 se não for carrossel) | `data.carousel_media_count` |
| `legenda` | Texto da legenda, com quebras de linha trocadas por espaço | `data.caption.text` |
| `hashtags` | Hashtags da legenda, separadas por espaço | extraídas da legenda |
| `mencoes` | @ mencionados na legenda, separados por espaço | extraídos da legenda |
| `coautores` | @ que assinam junto (post em colaboração) | `data.coauthor_producers` |
| `curtidas` | Número de curtidas. Vazio quando o perfil oculta curtidas | `data.like_count` |
| `comentarios` | Número de comentários (só a contagem, nunca o texto) | `data.comment_count` |
| `visualizacoes` | Visualizações do vídeo, quando a plataforma informa | `data.view_count` |
| `reproducoes` | Reproduções do vídeo. Só vem da aba Reels do perfil | `data.play_count` |
| `parceria_paga` | `True` se a plataforma marca como parceria paga | `data.is_paid_partnership` |
| `fixado` | `True` se o post está fixado no topo do perfil | `data.timeline_pinned_user_ids` |
| `data_coleta` | Quando o post foi capturado pela extensão | `timestamp_collected` |
| `arquivo_origem` | Nome do `.ndjson` de onde a linha veio | nome do arquivo |

## Valores vazios

Vazio não é zero. Curtidas vazias costumam ser curtidas ocultas pelo perfil; reproduções vazias costumam ser vídeo que não apareceu na aba Reels (colaboração com outra conta, por exemplo). Mantenha vazio e declare no texto.

## `dados_brutos/seguidores.csv`

| Coluna | O que é |
|---|---|
| `data` | Dia da anotação |
| `perfil` | O @ sem arroba |
| `seguidores` | Número exato lido no perfil naquele dia |

Dia sem anotação fica sem linha. Não preencha por estimativa sem dizer que é estimativa.

## `saida/transcricoes_<grupo>.csv`

| Coluna | O que é |
|---|---|
| `shortcode` | Código do post (liga com `posts_<grupo>.csv`) |
| `arquivo` | Nome do vídeo transcrito |
| `transcricao` | Texto falado. Vazio = sem fala (música) ou sem áudio |

## `saida/planilha_<data>_<hora>.xlsx`

| Aba | Conteúdo |
|---|---|
| `leia_me` | Data e hora de geração, período, dicionário de colunas |
| `resumo` | Por grupo e formato: posts, média e mediana de curtidas e comentários, média de reproduções |
| `<grupo>` | Todos os posts da coleta do grupo |
| `transcricoes` | shortcode, arquivo, texto (se você passou `--transcricoes`) |
| `dias_sem_post` | Dias do período sem nenhum post, por grupo |

## `documentos/dias_sem_post.csv`

Você preenche à mão (ou a IA preenche, e você confere): `dia`, `grupo`, `classificacao` (`tem_post_fora_da_base`, `fuso_diferente`, `sem_post`, `nao_concluido`), `evidencia`, `fonte`.
