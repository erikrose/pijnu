# -*- coding: utf-8 -*-


''' © copyright 2009 Denis Derman
	contact: denis <dot> spir <at> free <dot> fr
	
    This file is part of PIJNU.
	
    PIJNU is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
	
    PIJNU is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
	
    You should have received a copy of the GNU General Public License
    along with PIJNU: see the file called 'GPL'.
    If not, see <http://www.gnu.org/licenses/>.
	'''
valid_operands = {
        # ----- Strings
        '"oneword"': String("oneword"),
        '"double quotes"': String("double quotes"),
        "'single quotes'": String("single quotes"),
        "''": String(""),
        '""': String(""),
        "'something with \"quotes\"'": String('something with "quotes"'),
        '"something with \'quotes\'"': String("something with 'quotes'"),
        u'"áéíóúñçÁÉÍÓÚÑÇ"': String(u"áéíóúñçÁÉÍÓÚÑÇ"),
        u'"海納百川，有容乃大"': String(u"海納百川，有容乃大"),
        u"'مقالة مختارة'": String(u"مقالة مختارة"),
        u'"вільної енциклопедії"': String(u"вільної енциклопедії"),
        # ----- Numbers
        '1': Number(1),
        '01': Number(1),
        '5000': Number(5000),
        '+3': Number(3),
        '-3': Number(-3),
        '2.34': Number(2.34),
        '2.2': Number(2.2),
        '+3.1416': Number(3.1416),
        '-3.1416': Number(-3.1416),
        '5,000': Number(5000),
        '1,000,000.34': Number(1000000.34),
        '+1,000,000.22': Number(1000000.22),
        '-1,000,000.22': Number(-1000000.22),
        # ----- Variables:
        'today': Variable("today"),
        'camelCase': Variable("camelCase"),
        'with_underscore': Variable("with_underscore"),
        ' v1 ': Variable("v1"),
        'var1_here': Variable("var1_here"),
        u'résumé': Variable(u"résumé"),
        u'有容乃大': Variable(u"有容乃大"),
        '    spaces': Variable("spaces"),
        'spaces    ': Variable("spaces"),
        '  spaces  ': Variable("spaces"),
        '_protected_var': Variable("_protected_var"),
        '__private_var': Variable("__private_var"),
        'one_underscore': Variable("one_underscore"),
        'two__underscores__here': Variable("two__underscores__here"),
        'case_insensitive_var': Variable("CASE_INSENSITIVE_VAR"),
        'CASE_INSENSITIVE_VAR': Variable("case_insensitive_var"),
        'cAsE_iNsEnSiTiVe_VaR': Variable("CaSe_InSeNsItIvE_vAr"),
        u'MAYÚSCULA_minúscula_AQUÍ': Variable(u"mayúscula_MINÚSCULA_aquí"),
        # ----- Sets:
        ' {} ': Set(),
        '{{}, {}}': Set(Set(), Set()),
        '{1,000, 3.05}': Set(Number(1000), Number(3.05)),
        '{1,234,567}': Set(Number(1234567)),
        '{23,24,25}': Set(Number(23), Number(24), Number(25)),
        '{100, 200, 300}': Set(Number(100), Number(200), Number(300)),
        '{var1, var2}': Set(Variable("var1"), Variable("var2")),
        '{var, "string"}': Set(Variable("var"), String("string")),
        '{3, var, "string"}': Set(Number(3), String("string"), Variable("var")),
        '{1, 2, {"orange", "apple"}, 3}': Set(
            Number(1),
            Number(2),
            Number(3),
            Set(String("orange"), String("apple"))
            ),
        u'{"españa", {"caracas", {"las chimeneas", "el trigal"}}, "france"}': \
            Set(
                String(u"españa"),
                String("france"),
                Set(
                    String("caracas"),
                    Set(String("el trigal"), String("las chimeneas"))
                ),
            ),
    }
