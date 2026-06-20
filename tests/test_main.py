from main import construir_parser


def test_parser_valores_por_defecto():
    args = construir_parser().parse_args([])
    assert args.vista == "terminal"
    assert args.dt == 1.0


def test_parser_elige_matplotlib():
    args = construir_parser().parse_args(["--vista", "matplotlib"])
    assert args.vista == "matplotlib"


def test_parser_dt_personalizado():
    args = construir_parser().parse_args(["--dt", "2.5"])
    assert args.dt == 2.5


def test_parser_vista_invalida():
    import pytest
    with pytest.raises(SystemExit):
        construir_parser().parse_args(["--vista", "web"])


def test_parser_semilla_default_none():
    args = construir_parser().parse_args([])
    assert args.semilla is None


def test_parser_semilla_personalizada():
    args = construir_parser().parse_args(["--semilla", "7"])
    assert args.semilla == 7
