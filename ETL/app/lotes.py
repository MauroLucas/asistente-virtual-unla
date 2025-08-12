def get_lotes_config():
    """
    Devuelve la lista de lotes a registrar.
    """
    lotes = [
        {
            "lote_key": 1,
            "lote_descripcion": "Carga Excel Materias",
            "lote_esquema": "data",
            "lote_origen": "EXCEL",
        },
        {
            "lote_key": 2,
            "lote_descripcion": "Carga Excel Consejos de Materias",
            "lote_esquema": "data",
            "lote_origen": "EXCEL",
        },
    ]
    return lotes
