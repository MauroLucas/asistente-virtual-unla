def get_lotes_config():
    """
    Devuelve la lista de lotes a registrar.
    """
    lotes = [
        {
            "lote_key": 1,
            "lote_descripcion": "Carga Excel Materias Sistemas Plan 2024",
            "lote_esquema": "data",
            "lote_origen": "EXCEL",
        },
        {
            "lote_key": 2,
            "lote_descripcion": "Carga Excel Consejos de Materias",
            "lote_esquema": "data",
            "lote_origen": "EXCEL",
        },
       
        {
            "lote_key": 3,
            "lote_descripcion": "Carga Excel Materias Sistemas Plan 2014",
            "lote_esquema": "data",
            "lote_origen": "EXCEL",
        },

        {
            "lote_key": 4,
            "lote_descripcion": "Carga Programas/Contenidos desde Word (Drive)",
            "lote_esquema": "data",
            "lote_origen": "DRIVE_DOCX",
        },
    ]
    return lotes

