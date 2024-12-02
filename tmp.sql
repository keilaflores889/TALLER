SELECT
    am.id_agenda_medica
    , am.id_turno
    , t.descripcion
FROM
    agenda_medica am
LEFT JOIN turno t ON t.id_turno = am.id_turno