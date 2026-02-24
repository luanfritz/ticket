from app.models import MilesProgram


MILES_REFERENCE_BRL = {
    MilesProgram.latam_pass: 0.028,
    MilesProgram.smiles: 0.023,
    MilesProgram.tudo_azul: 0.02,
}


def is_miles_good_deal(value_per_mile_brl: float | None, program: MilesProgram | None) -> bool:
    if value_per_mile_brl is None or program is None:
        return False
    return value_per_mile_brl >= MILES_REFERENCE_BRL[program]
