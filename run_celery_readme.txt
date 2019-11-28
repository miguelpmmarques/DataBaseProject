1º - pip install dos requirements
2º- migrações ( don't worry são tableas novas que n fodem nada. Mas eu fiz uma mudançazita nos models)
3º abram uma consola dentro do env e façam cd para a pasta UniLeague
4º corram a instrução "celery -A UniLeague beat"
5º repitam o ponto 3 com uma nova shell
6º corram o comando "celery -A UniLeague worker --loglevel=info"
7º sorriam seus ********
