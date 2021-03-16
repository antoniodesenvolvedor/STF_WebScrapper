CREATE DATABASE db_automacoes


CREATE TABLE tb_jurisprudencia (
id int not null primary key identity(1,1),
datacad datetime not null,
decisao varchar(max),
ementa varchar(max),
data_publicacao varchar(15),
tema varchar(max),
tese varchar(max),
data_julgamento varchar(15),
classe_processual varchar(500),
doutrina varchar(max),
relator varchar(500)
)

CREATE TABLE tb_partes (
id int not null identity(1,1) primary key,
datacad datetime,
tipo varchar(255),
nome varchar(2000),
id_tb_jurisprudencia int not null foreign key references tb_jurisprudencia(id)

)





