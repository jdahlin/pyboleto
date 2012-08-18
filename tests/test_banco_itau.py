# -*- coding: utf-8 -*-
import datetime
import decimal
import unittest

from pyboleto.bank.itau import BoletoItau

from testutils import BoletoTestCase


class TestBancoItau(BoletoTestCase):
    def setUp(self):
        self.dados = []
        for i in range(3):
            d = BoletoItau()
            d.carteira = '109'
            d.agencia_cedente = '0293'
            d.conta_cedente = '01328'
            d.data_vencimento = datetime.date(2009, 10, 19)
            d.data_documento = datetime.date(2009, 10, 19)
            d.data_processamento = datetime.date(2009, 10, 19)
            d.valor_documento = 29.80
            d.nosso_numero = str(157 + i)
            d.numero_documento = str(456 + i)
            self.dados.append(d)

    def test_linha_digitavel(self):
        self.assertEqual(self.dados[0].linha_digitavel,
            '34191.09008 00015.710296 30132.800001 9 43950000002980'
        )

    def test_codigo_de_barras(self):
        self.assertEqual(self.dados[0].barcode,
            '34199439500000029801090000015710293013280000'
        )

    def test_agencia(self):
        self.assertEqual(self.dados[0].agencia_cedente, '0293')

    def test_conta(self):
        self.assertEqual(self.dados[0].conta_cedente, '01328')

    def test_dv_nosso_numero(self):
        self.assertEqual(self.dados[0].dv_nosso_numero, 1)

    def test_dv_agencia_conta_cedente(self):
        self.assertEqual(self.dados[0].dv_agencia_conta_cedente, 0)

    def test_boleto_props(self):
        props = self.dados[0].get_boleto_props()
        self.assertEquals(len(props), 4)
        self.assertEquals(props[0].name, 'agencia_cedente')
        self.assertEquals(props[1].name, 'carteira')
        self.assertEquals(props[2].name, 'conta_cedente')
        self.assertEquals(props[3].name, 'nosso_numero')

    def testArquivo(self):
        boleto = BoletoItau()
        boleto.carteira = '109'
        boleto.especie_documento = 8
        boleto.aceite = 'A'
        boleto.data_vencimento = datetime.date(2012, 7, 30)
        boleto.data_documento = datetime.date(2012, 6, 27)
        boleto.data_processamento = datetime.date(2009, 10, 19)
        boleto.valor_documento = decimal.Decimal("100.00")
        boleto.nosso_numero = '99999999'
        boleto.numero_documento = '9999999999'

        # Cedente
        boleto.agencia_cedente = '4459'
        boleto.conta_cedente = '17600'
        boleto.cedente = u'TRACY TECNOLOGIA LTDA ME'
        boleto.cedente_documento = 15594050000111
        boleto.cedente_tipo_documento = 'CNPJ'

        # Sacado
        boleto.sacado_nome =  u'JESUS DO CEU'
        boleto.sacado_documento = 83351622120
        boleto.sacado_tipo_documento = 'CPF'
        boleto.sacado_cidade = u'PARAISO DE DEUS'
        boleto.sacado_uf = 'SP'
        boleto.sacado_endereco = u'RUA AVENIDA DO CEU, 666'
        boleto.sacado_bairro = u'JD PARAISO'
        boleto.sacado_cep = '60606666'

        # FIXME: Standardize this and move to BoletoData
        boleto.identificacao_titulo = u'BOLETO DE TESTE'
        boleto.codigo_protesto = 3
        boleto.juros_mora_taxa_dia = decimal.Decimal('2.00')

        data = datetime.datetime(2012, 6, 27, 11, 20, 0)
        remessa = boleto.cnab240_remessa(contador=900002, data=data)
        self.check_remessa(remessa)

suite = unittest.TestLoader().loadTestsFromTestCase(TestBancoItau)

if __name__ == '__main__':
    unittest.main()
