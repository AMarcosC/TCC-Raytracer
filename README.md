# TCC-Raytracer

## Exemplos

Exemplos para demonstração do código estão presentes na pasta "legacy-examples". A execução do exemplo necessita da instalação das bibliotecas presentes em **requirements.txt**. Para instalar as dependências, basta executar *pip install -r requirements.txt* (o uso de um *virtual environment* é recomendado).

Executando-se **legacy-examples/raytracer - modelo 01/Raytracer.py**, serão obtidos os resultados presentes
no TCC 01:

~~~
- Dados do exemplo:
    - Modelo: telhado simples, separado entre o modelo tridimensional do telhado (assets/Telhado-Telhado.obj)
    e o modelo tridimensional do resto da casa, nesse caso, basicamente, as paredes (assets/Telhado-Parede.obj)
    - Localidade: Juazeiro do Norte-CE
    - Data: 04/07/2022, de 07h às 14h
    - Dados de azimute e elevação obtidos do site sunearthtools.com (comentar as entradas da lista no fim
    do código para diminuir o tempo de execução)

- Output do exemplo (em output):
    - 8 fotos correspondentes à renderização utilizando ray-tracing, para cada hora do dia
    - 1 foto correspondente ao campo escelar de sombreamento.
~~~

## Versão atual

Os arquivos soltos na pasta raíz do repositório, como também as pastas *teste*, *assets* e *output*, são as versões que estão sendo constantemente modificadas.


## Recursos adicionados recentemente

- Alterar a área de alcance da tela baseado no tamanho do modelo tridimensional (tornar a tela maior ou menor, ou reposicionar a tela, de forma que todo o modelo apareça nas imagens, mas que também não fique pequeno);
- Placas multicoloridas (cor escolhida aleatoriamente).

## Melhorias Pendentes

- Aplicar Multiprocessamento e/ou uso da GPU no processamento do traçado de raios;
- Processar o ray-tracing apenas na área de interesse, agilizando o código.
