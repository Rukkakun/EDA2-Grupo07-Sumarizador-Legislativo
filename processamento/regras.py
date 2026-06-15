import re

# Sufixos conjugados → sufixo do infinitivo
# Ordem importa: mais específicos primeiro
_REGRAS_VERBAIS = [
    (r"ando$", "ar"),
    (r"endo$", "er"),
    (r"indo$", "ir"),
    (r"ado$", "ar"),
    (r"ido$", "ir"),
    (r"armos$", "ar"), (r"ardes$", "ar"), (r"arem$", "ar"),
    (r"ermos$", "er"), (r"erdes$", "er"), (r"erem$", "er"),
    (r"irmos$", "ir"), (r"irdes$", "ir"), (r"irem$", "ir"),
    (r"assemos$", "ar"), (r"assem$", "ar"), (r"asse$", "ar"),
    (r"essemos$", "er"), (r"essem$", "er"), (r"esse$", "er"),
    (r"issemos$", "ir"), (r"issem$", "ir"), (r"isse$", "ir"),
    (r"emos$", "ar"),
    (r"em$", "ar"),
    (r"e$", "ar"),
    (r"amos$", "ar"),
    (r"amos$", "ar"),
    (r"aram$", "ar"), (r"ou$", "ar"),
    (r"eram$", "er"), (r"eu$", "er"),
    (r"iram$", "ir"), (r"iu$", "ir"),
    (r"amos$", "ar"), (r"am$", "ar"),
    (r"emos$", "er"), (r"em$", "er"),
    (r"imos$", "ir"), (r"em$", "ir"),
    (r"avas$", "ar"), (r"ava$", "ar"), (r"avamos$", "ar"), (r"avam$", "ar"),
    (r"ias$", "er"),  (r"ia$", "er"),  (r"iamos$", "er"), (r"iam$", "er"),
]

VERBOS_IRREGULARES = {
    # ver
    "vejo": "ver", "ves": "ver", "ve": "ver", "vemos": "ver", "veem": "ver",
    "via": "ver", "vias": "ver", "viamos": "ver", "viam": "ver",
    "vi": "ver", "viste": "ver", "viu": "ver", "viram": "ver",
    "veja": "ver", "vejas": "ver", "vejamos": "ver", "vejam": "ver",
    # dizer
    "digo": "dizer", "dizes": "dizer", "diz": "dizer", "dizemos": "dizer", "dizem": "dizer",
    "dizia": "dizer", "disse": "dizer", "dissemos": "dizer", "disseram": "dizer",
    "diga": "dizer", "digas": "dizer", "digamos": "dizer", "digam": "dizer",
    # fazer
    "faco": "fazer", "faz": "fazer", "fazemos": "fazer", "fazem": "fazer",
    "fazia": "fazer", "fiz": "fazer", "fez": "fazer", "fizemos": "fazer", "fizeram": "fazer",
    "faca": "fazer", "facam": "fazer",
    # ir
    "vou": "ir", "vai": "ir", "vao": "ir",
    "ia": "ir", "ias": "ir", "iamos": "ir", "iam": "ir",
    "fui": "ir", "foi": "ir", "fomos": "ir", "foram": "ir",
    "va": "ir", "vas": "ir",
    # ser
    "sou": "ser", "somos": "ser", "sao": "ser",
    "era": "ser", "eras": "ser", "eramos": "ser", "eram": "ser",
    "fui": "ser", "foi": "ser", "fomos": "ser", "foram": "ser",
    "seja": "ser", "sejam": "ser",
    # estar
    "estou": "estar", "esta": "estar", "estamos": "estar", "estao": "estar",
    "estava": "estar", "estavam": "estar",
    "esteve": "estar", "estiveram": "estar",
    "esteja": "estar", "estejam": "estar",
    # ter
    "tenho": "ter", "tens": "ter", "tem": "ter", "temos": "ter",
    "tinha": "ter", "tinhas": "ter", "tinhamos": "ter", "tinham": "ter",
    "tive": "ter", "teve": "ter", "tivemos": "ter", "tiveram": "ter",
    "tenha": "ter", "tenham": "ter",
    # poder
    "posso": "poder", "podes": "poder", "pode": "poder", "podemos": "poder", "podem": "poder",
    "podia": "poder", "puderam": "poder",
    "possa": "poder", "possam": "poder",
    # querer
    "quero": "querer", "queres": "querer", "quer": "querer", "queremos": "querer", "querem": "querer",
    "queria": "querer", "quis": "querer", "quisemos": "querer", "quiseram": "querer",
    "queira": "querer", "queiram": "querer",
    # vir
    "venho": "vir", "vens": "vir", "vem": "vir", "viemos": "vir",
    "vinha": "vir", "vim": "vir", "veio": "vir", "vieram": "vir",
    "venha": "vir", "venham": "vir",
}