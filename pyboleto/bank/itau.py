# -*- coding: utf-8 -*-
import datetime

from ..cnab240 import Remessa240
from ..data import BoletoData, boleto_prop

# Carteiras
#
# Documentação (verificado 18/08/2012)
# http://download.itau.com.br/bankline/cobranca_cnab240.pdf
#
# 102 SEM REGISTRO COM EMISSÃO INTEGRAL – CARNÊ
# 103 SEM REGISTRO COM EMISSÃO E ENTREGA – CARNÊ
# 104 ESCRITURAL ELETRÔNICA – CARNÊ
# 105 ESCRITURAL ELETRÔNICA - DÓLAR – CARNÊ
# 106 SEM REGISTRO COM EMISSÃO E ENTREGA - 15 DÍGITOS – CARNÊ
# 107 SEM REGISTRO COM EMISSÃO INTEGRAL - 15 DÍGITOS – CARNÊ
# 108 DIRETA ELETRÔNICA EMISSÃO INTEGRAL – CARNÊ
# 109 DIRETA ELETRÔNICA SEM EMISSÃO – SIMPLES
# 110 - " -
# 111 - " -
# 112 ESCRITURAL ELETRÔNICA - SIMPLES
# 113 ESCRITURAL ELETRÔNICA - TR – CARNÊ
# 116 ESCRITURAL CARNE COM IOF 0,38%
# 117 ESCRITURAL CARNE COM IOF 2,38%
# 119 ESCRITURAL CARNE COM IOF 7,38%
# 121 DIRETA ELETRÔNICA EMISSÃO PARCIAL - SIMPLES
# 134 ESCRITURAL COM IOF 0,38
# 135 ESCRITURAL COM IOF 2,38%
# 136 ESCRITURAL COM IOF 7,38%
# 147 ESCRITURAL ELETRÔNICA – DÓLAR
# 148 DIRETA COM IOF 0,38%
# 149 DIRETA COM IOF 2,38%
# 150 DIRETA ELETRÔNICA SEM EMISSÃO – DÓLAR
# 153 DIRETA COM IOF 7,38%
# 166 ESCRITURAL ELETRÔNICA – TR
# 167 SEM REGISTRO SEM EMISSAO COM IOF 0,38%
# 168 DIRETA ELETRÔNICA SEM EMISSÃO – TR
# 172 SEM REGISTRO COM EMISSÃO INTEGRAL
# 174 SEM REGISTRO EMISSÃO PARCIAL COM PROTESTO BORDERÔ
# 175 SEM REGISTRO SEM EMISSÃO
# 177 SEM REGISTRO EMISSÃO PARCIAL COM PROTESTO ELETRÔNICO
# 179 SEM REGISTRO SEM EMISSÃO COM PROTESTO ELETRÔNICO
# 180 DIRETA ELETRÔNICA EMISSÃO INTEGRAL – SIMPLES
# 191 DUPLICATAS - TRANSFERÊNCIA DE DESCONTO
# 195 SEM REGISTRO COM EMISSÃO INTEGRAL - 15 DÍGITOS
# 196 SEM REGISTRO COM EMISSÃO E ENTREGA - 15 DÍGITOS
# 198 SEM REGISTRO SEM EMISSÃO 15 DÍGITOS
# 202 SEM REGISTRO SEM EMISSAO COM IOF 2,38%
# 203 SEM REGISTRO SEM EMISSAO COM IOF 7,38%
# 204 SEM REGISTRO COM EMISSAO COM IOF 0,38%
# 205 SEM REGISTRO COM EMISSAO COM IOF 2,38%
# 206 SEM REGISTRO COM EMISSAO COM IOF 7,38%
# 210 DIRETA ELETRÔNICA SEM EMISSÃO – CONTRATUAL
# 212 ESCRITURAL ELETRÔNICA - CONTRATUAL
# 221 DIRETA ELETRÔNICA EMISSÃO PARCIAL - CONTRATUAL
# 280 DIRETA ELETRÔNICA EMISSÃO INTEGRAL – CONTRATUAL

# ESPÉCIE (especio documento, não é de moeda)
# 01 DUPLICATA MERCANTIL
# 02 NOTA PROMISSÓRIA
# 03 NOTA DE SEGURO
# 04 MENSALIDADE ESCOLAR
# 05 RECIBO
# 06 CONTRATO
# 07 COSSEGUROS
# 08 DUPLICATA DE SERVIÇO
# 09 LETRA DE CÂMBIO
# 13 NOTA DE DÉBITOS
# 15 DOCUMENTO DE DÍVIDA
# 16 ENCARGOS CONDOMINIAIS
# 17 CONTA DE PRESTAÇÃO DE SERVIÇOS
# 99 DIVERSOS

# PROTESTO
# 0 – Sem instrução
# 1 – Protestar (Dias Corridos)
# 2 – Protestar (Dias Úteis)
# 3 – Não protestar


class BoletoItau(BoletoData):
    '''Implementa Boleto Itaú

        Gera Dados necessários para criação de boleto para o banco Itau
        Todas as carteiras com excessão das que utilizam 15 dígitos: (106,107,
        195,196,198)
    '''

    # Nosso numero (sem dv) com 8 digitos
    nosso_numero = boleto_prop('nosso_numero', 8,
                               title='Nosso numero')

    # Conta (sem dv) com 5 digitos
    conta_cedente = boleto_prop('conta_cedente', 5,
                                title='Conta cedente')

    # Carteira (sem dv) com 3 digitos
    carteira = boleto_prop('carteira', 3,
                           title='Carteira')

    def __init__(self):
        super(BoletoItau, self).__init__()

        self.codigo_banco = "341"
        self.logo_image = "logo_itau.jpg"
        self.especie_documento = 'DM'

    @property
    def dv_nosso_numero(self):
        composto = "%4s%5s%3s%8s" % (self.agencia_cedente, self.conta_cedente,
                                     self.carteira, self.nosso_numero)
        return self.modulo10(composto)

    @property
    def dv_agencia_conta_cedente(self):
        agencia_conta = "%s%s" % (self.agencia_cedente, self.conta_cedente)
        return self.modulo10(agencia_conta)

    @property
    def agencia_conta_cedente(self):
        return "%s/%s-%s" % (self.agencia_cedente, self.conta_cedente,
                             self.dv_agencia_conta_cedente)

    def format_nosso_numero(self):
        return "%3s/%8s-%1s" % (self.carteira, self.nosso_numero,
                                self.dv_nosso_numero)

    @property
    def campo_livre(self):
        content = "%3s%8s%1s%4s%5s%1s%3s" % (self.carteira,
                                             self.nosso_numero,
                                             self.dv_nosso_numero,
                                             self.agencia_cedente,
                                             self.conta_cedente,
                                             self.dv_agencia_conta_cedente,
                                             '000'
                                             )
        return content

    def cnab240_remessa(self, contador, data=None):
        if data is None:
            data = datetime.today()

        if self.carteira not in ['108', '109', '110', '111']:
            raise TypeError("Carteira não suportada: %s" % (self.carteira, ))

        remessa = Remessa240()
        remessa.addicionar_cobranca(self)

        # Pagina 6
        cedente_tipo = 1 if self.cedente_tipo_documento == 'CPF' else 2
        remessa.header[1:3] = self.codigo_banco
        remessa.header[4:7] = 0
        remessa.header[8:8] = '0'
        remessa.header[18:18] = cedente_tipo
        remessa.header[19:32] = self.cedente_documento
        remessa.header[53:53] = 0
        remessa.header[54:57] = self.agencia_cedente
        remessa.header[59:65] = 0
        remessa.header[66:70:int] = self.conta_cedente
        remessa.header[72:72] = self.dv_agencia_conta_cedente
        remessa.header[73:102] = self.cedente
        remessa.header[103:132] = "BANCO ITAU SA"
        remessa.header[143:143] = "1"  # 1 = Remessa, 2 = Retorno
        remessa.header[144:151] = data.strftime('%d%m%Y')
        remessa.header[152:157] = data.strftime('%H%M%S')
        remessa.header[158:163] = contador
        remessa.header[164:168] = "040"
        # Especificação está errada, deveria ser brancos, não zeros
        # remessa.header[167:171] = 0
        # remessa.header[226:228] = 0

        # Pagina 7
        codigo_lote = 1
        remessa.header_lote[1:3] = self.codigo_banco
        remessa.header_lote[4:7] = codigo_lote
        remessa.header_lote[8:8] = '1'
        remessa.header_lote[9:9] = 'R'
        remessa.header_lote[10:11] = '01'
        remessa.header_lote[12:13] = 0
        remessa.header_lote[14:16] = '030'
        remessa.header_lote[18:18] = cedente_tipo
        remessa.header_lote[19:33] = self.cedente_documento
        remessa.header_lote[54:54] = 0
        remessa.header_lote[55:58] = self.agencia_cedente
        remessa.header_lote[60:66] = 0
        remessa.header_lote[67:71] = self.conta_cedente
        remessa.header_lote[73:73] = self.dv_agencia_conta_cedente
        remessa.header_lote[74:103] = self.cedente
        remessa.header_lote[184:191] = str(contador) + str(codigo_lote).zfill(2)
        remessa.header_lote[192:199] = data.strftime('%d%m%Y')
        remessa.header_lote[200:207] = 0

        # Pagina 8
        remessa.p[1:3] = self.codigo_banco
        remessa.p[4:7] = 1
        remessa.p[8:8] = '3'
        remessa.p[9:13] = codigo_lote
        remessa.p[14:14] = 'P'
        remessa.p[16:17] = Remessa240.CODIGO_OCORRENCIA
        remessa.p[18:18] = 0
        remessa.p[19:22] = self.agencia_cedente
        remessa.p[24:30] = 0
        remessa.p[31:35] = self.conta_cedente
        remessa.p[37:37] = self.dv_agencia_conta_cedente
        remessa.p[38:40] = self.carteira
        remessa.p[41:48] = self.nosso_numero
        remessa.p[49:49] = self.dv_nosso_numero
        remessa.p[58:62] = 0
        remessa.p[63:72] = self.numero_documento
        remessa.p[78:85] = self.data_vencimento.strftime('%d%m%Y')
        remessa.p[86:100] = self._valor_documento
        remessa.p[101:105] = 0
        remessa.p[106:106] = 0
        remessa.p[107:108] = self.especie_documento
        remessa.p[109:109] = self.aceite
        remessa.p[110:117] = self.data_documento.strftime('%d%m%Y')
        remessa.p[118:196] = 0
        remessa.p[127:141] = self.juros_mora_taxa_dia
        remessa.p[196:220] = self.identificacao_titulo
        remessa.p[221:221] = self.codigo_protesto
        remessa.p[222:223] = 0
        remessa.p[224:224] = 0
        remessa.p[225:226] = 0
        remessa.p[227:239] = 0

        # Pagina q
        remessa.q[1:3] = self.codigo_banco
        remessa.q[4:7] = codigo_lote
        remessa.q[8:8] = '3'
        remessa.q[9:13] = 2  # numero de registros no lote, p & q
        remessa.q[14:14] = 'Q'
        remessa.q[16:17] = Remessa240.CODIGO_OCORRENCIA
        remessa.q[18:18] = 1 if self.sacado_tipo_documento == 'CPF' else 2
        remessa.q[19:33] = self.sacado_documento
        remessa.q[34:63] = self.sacado_nome
        remessa.q[74:113] = self.sacado_endereco
        remessa.q[114:128] = self.sacado_bairro
        remessa.q[129:136] = self.sacado_cep
        remessa.q[137:151] = self.sacado_cidade
        remessa.q[152:153] = self.sacado_uf
        remessa.q[154:169] = 0
        remessa.q[210:212] = 0

        # Pagina 14
        remessa.trailer_lote[1:3] = self.codigo_banco
        remessa.trailer_lote[4:7] = codigo_lote
        remessa.trailer_lote[8:8] = '5'
        remessa.trailer_lote[18:23] = 4  # numero de registros do lote:
                                         # header, p, q, trailer
        remessa.trailer_lote[24:29] = 0
        remessa.trailer_lote[30:46] = 0
        remessa.trailer_lote[47:52] = 0
        remessa.trailer_lote[53:69] = 0
        remessa.trailer_lote[70:115] = 0

        # Pagina 14
        remessa.trailer[1:3] = self.codigo_banco
        remessa.trailer[4:7] = '9999'
        remessa.trailer[8:8] = '9'
        remessa.trailer[18:23] = len(remessa.lotes)
        remessa.trailer[24:29] = len(remessa.registros)

        return remessa
