# O que tentamos antes (e por que o método ficou assim)

Registro das escolhas, para você não repetir os tropeços. Tudo aqui vem da experiência de um projeto; a plataforma muda, então confira o que ainda vale.

## 1. Biblioteca que faz login e baixa post por post

Funcionou por algumas semanas, com pausas de 2 a 5 segundos entre pedidos. Depois a conta de pesquisa passou a receber bloqueios temporários ("aguarde alguns minutos", pedido de login repetido). Aumentar a pausa para 10 a 20 segundos ajudou, mas a coleta de perfis grandes ficou lenta demais e a conta continuou em risco.

O que ficou: pausas longas e parar na hora em que aparece bloqueio. Não insistir no mesmo dia.

## 2. Serviço pago por resultado (sem usar a conta)

Resolve o bloqueio, porque não usa conta do Instagram. Custa por post e por comentário; com crédito gratuito dá para testar, mas uma campanha inteira com comentários sai caro. Ficou como reserva.

## 3. Firefox + Zeeschuimer (o método deste repositório)

É o que a própria plataforma manda para o navegador de quem está vendo o perfil. Não faz pedido extra, não custa nada e a conta de pesquisa se comporta como uma pessoa lendo. Virou o caminho principal.

Limites que aprendemos:
- A grade do perfil não traz reproduções de vídeo; a aba **Reels** traz. Por isso o método rola duas abas.
- Vídeos em colaboração com outra conta não aparecem na aba Reels do perfil: ficam sem reproduções. Declarar.
- A extensão não traz seguidores nem texto de comentários.
- Cada download acumula o que já foi capturado; clicar em **Delete** depois de baixar evita arquivos gigantes.

## 4. Comentários

Chegamos a coletar texto de comentários com o @ de quem escreveu trocado por um código. A orientação acadêmica dispensou a coleta por causa da proteção de dados pessoais. O método atual guarda só o número de comentários.

## 5. Stories

Somem em 24 horas e a extensão não captura. Tentamos coleta diária por script (bloqueios) e prints manuais (trabalhoso, incompleto). Ficou fora do escopo, como lacuna declarada.

## 6. Seguidores

A página pública às vezes responde a um pedido automático e às vezes recusa. O que funcionou foi anotar à mão, todo dia, o número que aparece ao passar o mouse sobre "seguidores" no perfil. Dias esquecidos ficam vazios; para o texto, usamos estimativa de fontes públicas de terceiros, sempre identificada como estimativa.

## 7. Transcrição dos vídeos

Para análise de conteúdo, transcrevemos o áudio dos vídeos com um modelo de reconhecimento de fala rodando no próprio computador (sem internet e sem custo). Precisa baixar os `.mp4` antes e instalar um pacote de Python. Não está nos scripts deste repositório porque depende de pacotes externos; se precisar, peça à IA uma versão com `faster-whisper`, modelo `small`, idioma `pt`.

## 8. Nunca sobrescrever

No começo, importar uma coleta nova atualizava a planilha antiga. Perdemos o histórico de como as métricas eram no dia anterior. Desde então, cada coleta é uma pasta nova e a comparação é feita por script (`--anterior`). Essa é a regra mais importante do método.
