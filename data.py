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
        "descrição": "A porta principal do Villas-Boas por onde você entrou. Está trancada e as luzes piscam fracamente.",
        "frente": "corredor",
        "itens": [],
        "inspecionaveis": {
            "porta": "A porta está trancada por fora. Uma grossa corrente de aço te impede de sair."
        }
    },
    "corredor": {
        "descrição": "Um corredor longo e sujo com cheiro de pizza azeda. Tem o balcão à direita, as salas de festa 01 e 02 à esquerda, sala do gerador (03) a frente, e o palco aos fundos.",
        "atrás": "entrada", "frente": "03", "direita": "balcão", "esquerda": "01",
        "01": "01", "02": "02", "03": "03", "palco": "palco",
        "itens": [],
        "inspecionaveis": {
            "02": "Uma pesada porta de ferro, parece estar trancada",
            "03": "Uma porta velha de madeira emperrada, a maçaneta parece quebrada."
        }
    },
    "balcão": {
        "descrição": "O lugar onde costumavam servir lanches. A máquina registradora está aberta e vazia, exceto por restos de doces mofados.",
        "esquerda": "corredor",
        "itens": ["doce", "tesoura quebrada", "pano"]
    },
    "palco": {
        "descrição": "Um palco mal iluminado. O chão está sujo. Atrás das cortinas vermelhas há uma porta dupla para a Sala de Jantar.",
        "frente": "sala de jantar",
        "itens": ["pedra", "fita isolante"]
    },
    "01": {
        "descrição": "A sala de festas 01. Mesas emborcadas e cadeiras quebradas. Tem uma cadeira intacta no canto, de frente aos monitores de Segurança antigos.",
        "direita": "corredor", "frente": "cadeira",
        "itens": ["tabua pequena de madeira"],
        "inspecionaveis": {
            "cadeira": "Uma cadeira de plástico resistente virada para um painel de segurança.",
            "cofre": "Um cofre de ferro robusto com um teclado numérico.",
            "monitores": "Os antigos monitores de câmera de segurança."
        },
        "cofre_important": True
    },
    "cadeira": {
        "descrição": "O sistema de segurança se liga. O ar gela.",
        "itens": []
    },
    "02": {
        "descrição": "A porta da Sala de Festas 02. Ela está trancada com um cadeado pesado. Talvez precise da chave da cozinha.",
        "direita": "corredor",
        "itens": []
    },
    "cozinha privada": {
        "descrição": "Uma cozinha industrial imunda. O cheiro do mofo é insuportável. No canto das sombras está o temido animatrônico 'Alberto Troll'.",
        "inspecionaveis": {
            "alberto": "Um animatrônico bizarro e assustador. Nas costas dele há um painel escrito: [ DESLIGAR ALBERTO ]."
        },
        "atrás": "corredor",
        "itens": ["remedio", "sanduiche estragado"]
    },
    "03": {
        "descrição": "A porta 03. O caminho para a sala de energia. Está emperrada.",
        "atrás": "corredor",
        "itens": []
    },
    "sala do gerador": {
        "descrição": "A antiga sala de energia (porta 03). O gerador principal está aqui. Há fios soltos e um painel exposto.",
        "atrás": "corredor",
        "itens": ["bateria nova", "disquete"]
    },
    "sala de jantar": {
        "descrição": "Um espaço enorme. As paredes são cheias de desenhos infantis macabros, do lado direito parece ter as antigas máquinas de fliperama.",
        "atrás": "palco", "direita": "sala de fliperamas", "esquerda": "porta dos fundos",
        "itens": ["papel", "recorte 2"]
    },
    "sala de fliperamas": {
        "descrição": "Uma sala poeirenta iluminada apenas pelos letreiros de neon piscantes de 3 velhas máquinas de fliperama ligadas ('jon', 'consertos', 'julgamento').",
        "esquerda": "sala de jantar",
        "itens": ["moeda velha", "recorte 3"],
        "inspecionaveis": {
            "maquinas": "Existem três máquinas com as telas acesas: 'jon', 'consertos' e 'julgamento'."
        }
    },
    "porta dos fundos": {
        "descrição": "Uma pesada porta de metal enferrujado que dá acesso aos fundos do restaurante.",
        "direita": "sala de jantar",
        "itens": []
    },
    "sala dos fundos": {
        "descrição": "Um corredor estreito e gélido. A frente há uma porta blindada para a verdadeira 'Sala de Energia'.",
        "frente": "sala de energia", "atrás": "sala de jantar",
        "itens": ["recorte 1", "isqueiro", "fosforo", "garrafa vazia"]
    },
    "sala de energia": {
        "descrição": "O painel principal. Fios de alta tensão cobrem a parede.",
        "atrás": "sala dos fundos",
        "itens": ["fios cortados"]
    },
    "morte": {
        "descrição": "Você está morto. O escuro engoliu sua alma.",
        "itens": []
    },
    "saida": {
        "descrição": "A luz da lua ilumina o estacionamento através da porta aberta.",
        "itens": []
    },
    "cama": {
        "descrição": "Você sente o cheiro dela.",
        "itens": []
    },
    "final_bom": {
        "descrição": "Um silêncio em paz domina o restaurante.",
        "itens": []
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
    "fita isolante": "Um rolo de fita preta grossa. A cola ainda deve servir.",
    "sanduiche estragado": "Um sanduíche de presunto de 2007. A carne já virou uma gosma cinza."
}