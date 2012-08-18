# -*- coding: utf-8 -*-
"""
    pyboleto.cnab240
    ~~~~~~~~~~~~~~~~

    Base para criação de arquivos CNAB240

    :copyright: © 2012 by Johan Dahlin, Davi Oliveira
    :license: BSD, see LICENSE for more details.

"""

import decimal
import unicodedata


class LinhaRemessa(object):
    def __init__(self, remessa, nome):
        self.nome = nome
        self.linha = [' '] * 240
        remessa.registros.append(self)

    def __repr__(self):
        return '<LinhaRemessa nome=%r>' % (self.nome, )

    def __setitem__(self, item, valor):
        if not isinstance(item, slice):
            raise TypeError

        tipo = item.step
        if tipo is None:
            tipo = type(valor)

        inicio = item.start - 1
        fim = item.stop
        tamanho = fim - inicio
        if tipo == unicode:
            valor = unicodedata.normalize(
                "NFKD", valor).encode('ascii', 'ignore')
            valor = valor.ljust(tamanho)
        elif tipo == str:
            valor = valor.ljust(tamanho)
        elif tipo == int:
            valor = str(valor).zfill(tamanho)
        elif tipo == decimal.Decimal:
            d = decimal.Decimal(valor * 100).quantize(0)
            valor = str(d).zfill(tamanho)
        else:
            raise TypeError("%r[%d:%d] = %r(%s)" % (
                self, item.start, item.stop, valor, tipo))

        if len(valor) != tamanho:
            raise AssertionError("%r[%d:%d]: %r(%d) != %d" % (
                self, item.start, item.stop,
                valor, len(valor), tamanho))
        self.linha[inicio:fim] = valor

    def como_string(self):
        return ''.join(self.linha)


class Remessa240(object):
    """
    Cada arquivo é composto dos seguintes registros, cada um tem
    240 bytes com \r\n no final.

    * um header de arquivo
    * um header de lote
    * detalhe
    * um trailer de lote
    * um trailer de arquivo

    """
    CODIGO_OCORRENCIA = 1

    def __init__(self):
        self.registros = []
        self.lotes = []
        self.boleto = None

    def addicionar_cobranca(self, boleto):
        self.header = LinhaRemessa(self, 'header')
        self.header_lote = LinhaRemessa(self, 'header_lote')
        self.p = LinhaRemessa(self, 'p')
        self.q = LinhaRemessa(self, 'q')
        self.trailer_lote = LinhaRemessa(self, 'trailer_lote')
        self.trailer = LinhaRemessa(self, 'trailer')
        self.lotes.append((self.header_lote,
                           self.trailer_lote))
        self.boleto = boleto

    def linhas(self):
        l = []
        for registro in self.registros:
            l.append(registro.como_string() + '\r\n')
        return l

    def dados_como_string(self):
        d = ''
        for registro in self.registros:
            d += registro.como_string() + '\r\n'
        return d
