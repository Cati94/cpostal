# cpostal
<------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------->
PROGRAMA:

É um programa que permite que o utilizador introduza um código postal português e a sua existência será verificada no csv. e na base de dados. A informação de distrito e concelho será completa (acrescentada) com base na API dos CTT.
 Caso o código postal não tenha informação na API ele informa o utilizador e se não existe na base de dados ou csv o código postal é procurado na API e acrescentado nas mesmas. 
<---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------->
RELATÓRIO DE ERROS:

Só podemos fazer 30 pedidos por minuto á API - senão erro 400/404/500;
Alguns códigos postais no csv não apresentam dados nos CTT API - Erro postal_code data not found in CTT API.
Testes unitários presentes no código fonte para check desde do código postal format/login/update or add to csv or db/db login.
API dos CTT - mostra ddos insuficientes de alguns códigos postais. 
Testes realizados: Inserir postal_code (do csv. e fora); Update e add to database and csv from CTT API.
<-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------->
REQUESITOS:
    Linguagem de programação utilizada: Python;
    Armazenamento de dados: Base de dados MySQL;
    Funciona tanto em windows como Linux;
    Usa MySQL e VS Studio Code Python 3.12.7;
<---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------->
LIBERIES:
    pandas as pd
    mysql.connector
    os
    requests
    re
    logging
<--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------->
#     I turn MSUD2 and cooler in code #
<---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------->
