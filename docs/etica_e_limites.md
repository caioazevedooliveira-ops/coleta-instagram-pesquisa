# Ética e limites

## O que o método coleta e o que não coleta

- Só **perfis públicos**, escolhidos pela pesquisa (figuras públicas, instituições, campanhas).
- Só **números e textos publicados pelo próprio perfil** (legenda, data, curtidas, contagem de comentários, reproduções).
- **Não coleta** texto de comentários, dados de quem comenta, mensagens, stories nem nada de perfis privados.
- Se um @ de pessoa comum aparecer (marcação, menção na legenda), ele vem junto na coluna `mencoes` ou `coautores`. Avalie com o orientador se deve ser mantido, anonimizado ou removido antes de qualquer publicação.

## Conta de pesquisa

Crie uma conta só para a pesquisa, com o nome do projeto ou do grupo. Nunca use a conta pessoal. A conta pode sofrer limitação temporária pela plataforma; quando isso acontecer, pare e espere.

## Ritmo

Pausa de 3 a 7 segundos entre rolagens, uma conta por vez, um perfil por vez. Mais rápido que isso é comportamento de robô e pode gerar bloqueio.

## O que ainda depende de você e do seu orientador

Confira antes de coletar. Nada aqui é parecer jurídico.

- [ ] **Termos de uso da plataforma:** leia a versão atual e registre a data da leitura.
- [ ] **LGPD (Lei 13.709/2018):** figura pública e dado publicado pela própria pessoa têm tratamento diferente de dado de terceiro. Confirme o enquadramento da sua pesquisa.
- [ ] **Comitê de ética:** veja se a sua instituição exige submissão para pesquisa com dados públicos de redes sociais.
- [ ] **Guarda dos dados:** onde ficam, por quanto tempo, quem acessa.

## O que declarar no texto final

- Período, perfis, fuso horário.
- Data e hora de cada coleta e quantos posts entraram em cada uma.
- As lacunas: reproduções ausentes, curtidas ocultas, dias sem post não concluídos, seguidores sem registro ou por estimativa, stories e comentários fora do escopo.
- Que a plataforma pode ter excluído posts entre uma coleta e outra (o `--anterior` mostra os que sumiram).

## O que nunca sobe para o repositório público

Dados brutos, planilhas, mídia, cookies, sessões, tokens, nome da conta de pesquisa. O `.gitignore` bloqueia os tipos comuns; confira com `git status` antes de cada `push`.
