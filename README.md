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

A execução de "PanelPlacer.py" pode resultar em erros, visto que esta versão ainda não tem nenhum exemplo fixo para testes.


## Recursos adicionados recentemente

- Alterar a área de alcance da tela baseado no tamanho do modelo tridimensional (tornar a tela maior ou menor, ou reposicionar a tela, de forma que todo o modelo apareça nas imagens, mas que também não fique pequeno);
- Placas multicoloridas (cor escolhida aleatoriamente).
- Mudança de orientação ao longo da varredura: o programa tem prioridade para inserir placas horizontalmente, mas se em algum lugar ele só conseguir colocar placas verticalmente, ele insere, a depender do desejo do usuário
- Varredura da imagem pode começar pelos quatro cantos da imagem (top-left, bottom-left, top-right, bottom-right)
- Placas podem ser inseridas com alinhamento relativo à primeira placa inserida (necessita de melhorias: resultados não são os esperados e o processamento aumenta em cerca de 2.5x)

## Melhorias Pendentes

- Aplicar Multiprocessamento e/ou uso da GPU no processamento do traçado de raios;
- Processar o ray-tracing apenas na área de interesse, agilizando o código.
- Correção das dimensões reais da placa ao mudar a orientação durante a locação
- Produzir arquivo com as coordenadas das placas para inserir no AutoCAD, por exemplo

## Última imagem produzida pelo programa

! [Ultima imagem](output/placas_overlay.png)
