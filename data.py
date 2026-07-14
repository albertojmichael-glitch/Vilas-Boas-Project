# ==========================================
# CONSTANTES DE JOGO
# ==========================================
COFRE_SENHA = "1994"
MAX_INVENTARIO = 3

# ==========================================
# ARTES ASCII
# ==========================================
CAVEIRA_MORTE = r'''
                     .ed"""" """$$$$be.
                   -"           ^""**$$$e.
                 ."                   '$$$c
                /                      "4$$b
               d  3                     $$$$
               $  * .$$$$$$
              .$  ^c           $$$$$e$$$$$$$$.
              d$L  4.         4$$$$$$$$$$$$$$b
              $$$$b ^ceeeee.  4$$ECL.F*$$$$$$$
  e$""=.      $$$$P d$$$$F $ $$$$$$$$$- $$$$$$
 z$$b. ^c     3$$$F "$$$$b   $"$$$$$$$  $$$$*"      .=""$c
4$$$$L   \     $$P"  "$$b   .$ $$$$$...e$$        .=  e$$$.
^*$$$$$c  %..   *c    ..    $$ 3$$$$$$$$$$eF     zP  d$$$$$
  "**$$$ec   "\   %ce""    $$$  $$$$$$$$$$* .r" =$$$$P""
        "*$b.  "c  *$e.    *** d$$$$$"L$$    .d"  e$$***"
          ^*$$c ^$c $$$      4J$$$$$% $$$ .e*".eeP"
             "$$$$$$"'$=e....$*$$**$cz$$" "..d$*"
               "*$$$  *=%4.$ L L$ P3$$$F $$$P"
                  "$   "%*ebJLzb$e$$$$$b $P"
                    %..      4$$$$$$$$$$ "
                     $$$e   z$$$$$$$$$$%
                      "*$c  "$$$$$$$P"
                       ."""*$$$$$$$$bc
                    .-"    .$***$$$"""*e.
                 .-"    .e$"     "*$c  ^*b.
          .=*""""    .e$*"          "*bc  "*$e..
        .$"        .z*"               ^*$e.   "*****e.
        $$ee$c   .d"                     "*$.        3.
        ^*$E")$..$"                         * .ee==d%
           $.d$$$* * J$$$e*
            """""                             "$$$"    
'''

ARTE_INDIO = r'''
                               ,,..,
                             ,@$$$$$.
                           .,$$$$$$$$i
                     .,z$""')$$$$$$$$C`^#`-..
                  ,zF'        `""#*"'       "*o.
               ,zXe>        u:..        ..      "c
             ,' zP'    ,:`"          .            "N.
           ,d",d$   ,'"   ,uB" .,uee..,?R.  ,  .    ^$.
         ,@P d$"     .:$$$$$$$$$$$$$@$CJN.,"    `     #b
        z$" d$P    :SM$$$$$$$$$$$$$$$$$$$Nf.           ^$.
       J$" J$P  , ,@$$$$$$$$$$$$$$$$$$$$$$$$$k.         "$r
      z$   $$.   ,$$$$$$$$$$$$$$$$$$$$$$$$$$f'   .    .   $b
     ,$"  $$u,-.x'^""$$$$$$$$$$$$$$$$$$$$$$$$$.        `.  $k
     $"  :$$$$> 8.   `#$$$$$$$$$$$$$$$$$$$$$"\  d  .    F   $.
    $P  .$$$$$N `$b.  $$$$$$$$$$$$$$$$$$$$$k.$  $"  :   '   `$
   <$'  4$$k $$c `*$.,Q$$$$$$$$$$$$$$$$$$$$$$$ ..            $L
   $P   4$$$$$F:   `"$$$$$$$$$$$$$$$$$$$$$$'`$"     .   ,    `$
  ,$'  ,$$$$$d$$    '##$$c3$$$$$$$$$$$$$$$$. '      :   L.    $.
  J$  u$$$$$$$$$.,oed$*$$$$N "#$$$$$$$$$$***$@$N. , $  ,B$$N.,9L
  $F,$$$$$$$$$$,@*"'  `J$$$$$#h$$$$$$P"`     `"*$$. $4W$' "$$uJF
  4$$$$$$$$$$$$F'      $*'`$$RR@$$$$$R        ,' "$d$4"    '$$$R
 ,$$$$$$$$$$$$$F     ,'    @$.3$$$$ R>            `$F$  dN.4$$$$.
:$$$$$$$$$$$$*$"          J$'$$$$$& $.             $'   $$$$$$$$$o
 ^$$$$$$$$$$B@$$          $P $$$"?N/$k             $r   $$P"*$$$$'
   $$i  .$$$$"$'         $$ ~R$P '$k^$$,'          $   "'  ,d$$'
   $$$$ J$$$$ `,'    .,z$P'd.$P   #$. #$$$u.       .$  eu. ,d$$$
   $^$$$$$$$$. `"=+=N#'.,d$M$$'   `$$@s.#$$$u.   ,$C  $$$@$$$"$
   "  `*$$$$$$bx..        ,M$"     `*$$$b/""$R"*"'d$ ,$$$$P"  '
   4     "$$k3$9$$B.e.  ,ud$F       `3$$$$b.      ,$,@R$*'    4
   <       *$$$$$$$b$$@$$$$$L   ,.  ,J$$.'**$$k$NX$"M"'       .
   $         "$#"  `" <$$$$$$c,z$N.,o$$$$   ,NW$*"'           $
   $.         ',    `$$$$$$$$$d$$$$$$$$$f ,$e*'                $
  ,$c         d.     `^$$$$$$$$$$$$$$$$$.u '"                :$.
  $$$         $\   .,  `"#$$$*$$$$$$$$$$$$ '                 4$F
  $$"         $ `  k.`.     ``"#`"""'      ,' ,'             `$$
  `"          $>,  `b.,ce(b:o uz CCLd$4$*F?\,o                "' 
              $&    $$k'*"$$$$$$#$$$$$$$$$$ d'
              $$.,$$$$$$$$,e,$#$.*$`""""'e4 $
              `$$$$  ^$$\$"$$$$$$$$$$$$$$$.eL
               $$$"  $$$$$$$e$.$.$$.$e$d$$$$k
               R`$$  '$$$$$$$$$$$$$$$$$$$$$$P
               `  $Nc'"$$N3$$$$$$$$$$$$$$$$$'  
                   *$  9$.`@$$$$$$$$$$R$$$#'
                    `$.  `"*$$$$$$$$$$P'' #
                      "$u.    `""""''   ,'
                        `"$Nu..  .,z
'''

ARTE_PORCO = r'''
      _.._                 ,.
    .' .-'`               (_|,.
   /  /      * ,' /, )_______   _
   |  |    * __j o``-'        `.'-)'
   \  \      * (")                 \'
    '._'-._           `-j                |
                        `-._(           /
                        |_\  |--^.  /
                          /_]'|_| /_)_/
                             /_]'  /_]'
'''

ARTE_ROBO = r'''
       .-T-.
      /     \
    }=) o o (={
      \_===_/
(_)  _.-"""-._
 |\/`/+' _ '+\`\
  \__\ +[_]+ /=|
      )====={\=\_
      |  .  | `( )
      |_/ \_|
     <__| |__>
      |=| |=|
      |_| |_|
     (___Y___)
'''

ARTE_PIANO = r'''
 ____________________________________
|\                                    \
| \                                    \
|  \____________________________________\
|  |       __---_ _---__                |
|  |      |======|=====|                |
|  |      |======|=====|                |
|  |  ____|__---_|_---_|______________  |
|  | |                                | |
|   \ \                                \ \
|  \ ||\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\| |     
|  |\  ,--------------------------------  |
|  ||| |                               || |
 \ ||| |           -  -                || |
  \'|| |-----------\\-\\---------------|| |
    \|_|            "  "               \|_|
'''

# ==========================================
# MAPA E DESCRIÇÕES
# ==========================================
MAPA_ORIGINAL = {
    "entrada": {
        "descrição": "você está na entrada do restaurante, está muito escuro, e as luzes piscam de forma ordenada, cheira mal",
        "frente": "sala de jantar",
        "inspecionaveis": {
            "poster": "Um pôster desbotado com os animatrônicos sorrindo: 'Bem-vindo ao Vilas Boas! Trazendo alegria desde 1982.'"
        },
        "direita": "hall de entrada",
        "atrás": "saida", 
        "esquerda": "parede velha",
        "itens": ["tabua pequena de madeira"]
    },
    "hall de entrada": {
        "descrição": "voce entra no hall de entrada, está um pouco mais claro, tem mesas de jantar, um balcão, e uma sala no fundo",
        "frente": "quarto de refrigeração",
        "direita": "balcão",
        "esquerda": "mesas de jantar",
        "atrás": "entrada",
        "itens": ["papel", "recorte 1"]
    },
    "balcão": {
        "descrição": "tem presentes, confetes, doces de áçucar e pelucias",
        "frente": "balcão",
        "direita": "balcão",
        "atrás": "hall de entrada",
        "esquerda": "balcão",
        "itens": ["tesoura quebrada", "pelucias", "doce", "moeda velha", "disquete"]
    },
    "quarto de refrigeração": {
        "descrição": "voce entra no quarto, está muito frio e os ventiladores fazem um barulho alto, tem um tubo de ventilação no centro da sala",
        "frente": "tubo de ventilação",
        "direita": "parede de ventiladores",
        "atrás": "hall de entrada",
        "esquerda": "parede de ventiladores",
        "itens": ["bateria nova"]
    },
    "tubo de ventilação": {
        "descrição": "você rasteja pelo aluminio gelado, você sente muito frio",
        "frente": "morte", 
        "direita": "aluminio",
        "atrás": "quarto de refrigeração",
        "esquerda": "aluminio",
        "itens": []
    },
    "sala de jantar": {
        "descrição": "tem varias mesas de jantar com confetes, é um lugar bem grande, está bem sujo",
        "inspecionaveis": {
            "jornal": "Caso Vilas Boas: Três desaparecimentos em 1994, seguem sem solução",
            "mesas": "Tem pedaços de papel, confetes coloridos, sujeira e algumas baratas."
        },
        "frente": "duas salas de festas",
        "direita": "corredor",
        "atrás": "entrada",
        "esquerda": "porta dos fundos", 
        "itens": ["confete", "isqueiro"]
    },
    "porta dos fundos": {
        "descrição": "Uma pesada porta de metal. Está trancada a chave.",
        "atrás": "sala de jantar",
        "frente": "Você empurra, mas não cede.",
        "itens": []
    },
    "corredor": {
        "descrição": "tem quatro portas, 01-sala de segurança | 02-porta trancada | 03-porta emperrada | 04-sala de intervalo",
        "01": "01",
        "02": "02",
        "03": "03",
        "04": "04",
        "atrás": "sala de jantar",
        "frente": "parede",
        "itens": []
    },
    "01": {
        "descrição": "voce entra na sala de segurança, tem um tubo de ventilação do canto esquerdo da sala, e tem uma mesa com ferramentas de segurança",
        "frente": "cadeira", 
        "cadeira": "cadeira",
        "atrás": "corredor",
        "inspecionaveis": {
            "papeis": "Tem muitos papeis encima da segunda mesa, emails e memorandos... algo chama atenção '1994..' são de 2007",
        },
        "esquerda": "nada",
        "direita": "nada",
        "cofre_important": "cofre",
        "itens": ["recorte 3", "disquete"]
    },
    "02": {
        "descrição": "porta trancada",
        "atrás": "corredor",
        "frente": "A porta te impede de avançar.",
        "esquerda": "parede",
        "direita": "corredor",
        "itens": []
    },
    "03": {
        "descrição": "porta emperrada",
        "atrás": "corredor",
        "frente": "Você força a porta com o braço, nada acontece.",
        "esquerda": "corredor",
        "direita": "parede",
        "itens": []
    },
    "04": {
        "descrição": "voce força a porta e consegue entrar, está escuro e você enxerga apenas a tubulação funcionando",
        "atrás": "corredor",
        "frente": "cama", 
        "esquerda": "parede",
        "direita": "parede",
        "itens": ["pano", "fosforo", "garrafa vazia"]
    },
    "sala do gerador": {
        "descrição": "A antiga sala de energia (porta 03). O gerador principal está aqui. Há fios soltos e um painel exposto.",
        "atrás": "corredor",
        "itens": []
    },
    "cozinha privada": {
        "descrição": "Uma cozinha industrial imunda. O cheiro do mofo é insuportável.",
        "atrás": "corredor",
        "itens": ["fita isolante"]
    },
    "duas salas de festas" : {
        "descrição": "voce avança e encontra duas salas festas, a sala 1 e sala 2, a sala 1 parece mais calma",
        "atrás": "sala de jantar",
        "sala 1": "sala 1",
        "sala 2": "sala 2",
        "esquerda": "corredor",
        "direita": "parede",
        "itens": ["pedra"]
    },
    "sala 1": {
        "descrição": "voce entra na sala de festas 1, está tudo parado e calmo. A uma sala de fliperamas a sua esquerda",
        "atrás": "duas salas de festas", 
        "frente": "palco",
        "direita": "sala 2",
        "esquerda": "sala de fliperamas",
        "itens": ["recorte 2"]
    },
    "sala de fliperamas": {
        "descrição": "O chão tem carpete neon sujo. Há três máquinas funcionando: 'fome de jon', 'consertos' e 'julgamento'. Digite 'jogar [nome]'.",
        "direita": "sala 1",
        "itens": []
    },
    "sala 2": {
        "descrição": "voce da de cara com um animatronico enorme no escuro! O zumbido cresce. Você tem poucos segundos para recuar!",
        "esquerda": "sala 1",
        "atrás": "duas salas de festas",
        "frente": "morte", 
        "direita": "morte", 
        "itens": []
    },
    "palco": {
        "descrição": "Você sobe no palco fedorento. As cortinas estão rasgadas. Algo terrível te observa nas sombras...",
        "atrás": "sala 1",
        "frente": "morte", 
        "itens": []
    },
    "sala dos fundos": {
        "descrição": "Um corredor denso e escuro. Há 5 portas com placas: 'pelucias', 'equipamento', 'animatronicos', 'mercadorias' e 'energia'.",
        "atrás": "sala de jantar",
        "esquerda": "cozinha principal",
        "pelucias": "sala de pelucias",
        "equipamento": "sala de equipamento",
        "animatronicos": "sala de animatronicos",
        "mercadorias": "sala de mercadorias",
        "energia": "sala de energia", 
        "itens": []
    },
    "cozinha principal": {
        "descrição": "A antiga cozinha que preparava comida. Tem uma caixa de primeiros socorros aberta.",
        "direita": "sala dos fundos",
        "itens": ["remedio", "pizza mofada"]
    },
    "sala de pelucias": {
        "descrição": "Uma sala cheia de pelúcias apodrecidas. Melhor não ficar aqui.",
        "atrás": "sala dos fundos",
        "itens": []
    },
    "sala de equipamento": {
        "descrição": "Apenas ferramentas velhas e graxa seca pelo chão.",
        "atrás": "sala dos fundos",
        "itens": ["bateria nova", "disquete"]
    },
    "sala de animatronicos": {
        "descrição": "Várias carcaças de metal desmontadas. Uma delas vira a cabeça devagar para você! Você bate a porta.",
        "atrás": "sala dos fundos",
        "itens": []
    },
    "sala de mercadorias": {
        "descrição": "Caixas de papelão mofadas com camisetas do restaurante.",
        "atrás": "sala dos fundos",
        "itens": []
    },
    "sala de energia": {
        "descrição": "Que quarto deprimente...",
        "inspecionaveis": {
            "celular quebrado": "Parece ser dela..."
        }
    }
}

descricoes_itens = {
    "tabua pequena de madeira": "Você passa a mão pela tábua, ela está velha, úmida, e cheia de farpas.",
    "tocha": "Você olha para a tábua com um papel procurando algo, mas não há nada.",
    "tocha acesa": "Você olha para a tocha acesa, parece que não vai durar muito pela umidade.",
    "papel": "O papel tem letras borradas de sangue: '1985'.",
    "papel aceso": "Você enxerga muito mais pela luz laranja do fogo, mas está queimando rápido.",
    "tesoura": "Tesoura escolar sem ponta, de aço inox, deve servir para arrombar alguma porta.",
    "tesoura quebrada": "Tesoura escolar quebrada, o aço entortou e perdeu o corte, está inútil.",
    "pelucias": "Pelúcias velhas e empoeiradas. Os olhos de plástico parecem te julgar na escuridão.",
    "doce": "Doce de laranja velho, grudado no plástico.",
    "confete": "Pedaços de papel colorido que perderam a cor. Têm cheiro de mofo.",
    "isqueiro": "Um isqueiro formidável dos anos 80, ainda está funcional.",
    "pano": "Pano velho cheio de pelo e sujeira, muito úmido.",
    "pano aceso": "O pano queima com uma chama irregular, cheirando a poeira queimada.",
    "fosforo": "Uma caixinha de fósforos quase vazia.",
    "garrafa vazia": "Uma garrafa de vinho suja.",
    "pedra": "Uma pedra comum e redonda. Pesada, fria e completamente inútil.",
    "moeda velha": "Uma ficha de fliperama enferrujada de 1982.",
    "chave da cozinha": "Uma chave prateada com um chaveiro sujo de graxa.",
    "remedio": "Um frasco de relaxante muscular, venceu em 1996. Talvez ajude com a dor.",
    "pizza mofada": "Um pedaço de pizza de 1994. Tem uma cor verde fluorescente.",
    "bateria nova": "Uma bateria industrial pesada. Cabe na sua lanterna",
    "recorte 1": "Pedaço de jornal de 1994: '...o cliente João Barros, desapareceu...' ",
    "recorte 2": "Parte central da notícia: '...a garçonete Ângela Silva vista pela última vez...' ",
    "recorte 3": "A base do jornal: '...o proprietário Renato Fidelis.'",
    "jornal completo": "Os três recortes unidos. Conta a história das três vítimas de 1994.",
    "lanterna": "Sua lanterna velha de plástico vermelha, você esqueceu de trocar a bateria antes de sair de casa.",
    "disquete": "Um disquete de 5¼ polegadas. Serve para salvar os dados do sistema no terminal.",
    "fita isolante": "Um rolo de fita preta grossa. A cola ainda deve servir."
}