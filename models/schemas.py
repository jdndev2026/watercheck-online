from sqlalchemy import Column, String, Integer, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from db.database import Base


class Watercheck(Base):

    __tablename__ = "watercheck"

    id                  = Column(String(10), primary_key=True)
    estandar_id         = Column(Integer, ForeignKey("estandaresTDS.id"), nullable=False)
    id_ultima_medicion  = Column(Integer, ForeignKey("mediciones.id"), nullable=False)
    correo_enviado_hoy  = Column(Integer, nullable=False, default=0)
    correo_usuario      = Column(String(200), nullable=False)
    
    relacion_mediciones = relationship( "Mediciones", back_populates="relacion_watercheck", cascade="all, delete-orphan", foreign_keys="Mediciones.watercheck_id" )
    relacion_estandar   = relationship( "EstandaresTDS", back_populates="relacion_watercheck" )


class Mediciones(Base):

    __tablename__ = "mediciones"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    watercheck_id = Column(String(10), ForeignKey("watercheck.id"), nullable=False)
    fecha         = Column(String(10), nullable=False)
    hora          = Column(String(8), nullable=False)
    tds           = Column(Float, nullable=False)
    turbidez      = Column(Float, nullable=False)
    ph            = Column(Float, nullable=False)
    estandar_id   = Column(Integer, ForeignKey("estandaresTDS.id"), nullable=False)

    relacion_watercheck = relationship( "Watercheck", back_populates="relacion_mediciones", foreign_keys=[watercheck_id] )
    relacion_estandar   = relationship( "EstandaresTDS", back_populates="relacion_mediciones" )

    __table_args__ = ( UniqueConstraint("watercheck_id", "fecha", "hora", name="medicion_unica"), )
    
    
class EstandaresTDS(Base):
    __tablename__ = "estandaresTDS"
    
    id        = Column(Integer, primary_key=True, autoincrement=True)
    estandar  = Column(String(15), nullable=False)
    mayor_que = Column(Float, nullable=False)
    menor_que = Column(Float, nullable=False)
    potable   = Column(Integer, nullable=False )
    color     = Column(String(10),nullable=False)
    
    relacion_watercheck = relationship("Watercheck", back_populates="relacion_estandar")
    relacion_mediciones = relationship("Mediciones", back_populates="relacion_estandar")