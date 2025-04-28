from sqlalchemy.exc import IntegrityError
from app.models.endereco import Endereco
from app.models.telefone import Telefone
from app.models.email import Email
from app import db
from datetime import datetime, timezone

class EntidadeService:

    @staticmethod
    def commit_endereco(entidade_id, consulta_id, logger, tipo_entidade_id, enderecos):
        if not enderecos:
            return

        # Apaga os endereços antigos de uma só vez
        Endereco.query.filter_by(entidade_id=entidade_id, tipo_entidade_id=tipo_entidade_id).delete()
        print(f"Endereços deletados para entidade_id={entidade_id}, tipo_entidade_id={tipo_entidade_id}")
        logger.add_log(
            mensagem=f"Endereços deletados para entidade_id={entidade_id}, tipo_entidade_id={tipo_entidade_id}",
            tipo_log="INFO",
            consulta_id=consulta_id,
            data_log=datetime.now(timezone.utc)
        )

        # Armazena novos endereços para inserção em lote
        novos_enderecos = []
        for endereco_id, endereco in enumerate(enderecos, start=1):
            logradouro = endereco.get('logradouro', "")
            complemento = endereco.get('complemento', "")
            bairro = endereco.get('bairro', "")
            cidade = endereco.get('cidade', "")
            cep = endereco.get('cep', "")
            
            novos_enderecos.append(Endereco(
                endereco_id=endereco_id,
                entidade_id=entidade_id,
                tipo_entidade_id=tipo_entidade_id,
                logradouro=logradouro[:100] if logradouro else "",
                numero=endereco.get('numero', None),
                complemento=complemento[:100] if complemento else "",
                bairro=bairro[:60] if bairro else "",
                cidade=cidade[:60] if cidade else "",
                uf=endereco.get('uf', None),
                cep=cep.replace('-', '') if cep else ""
            ))

        # Adiciona e comita em uma única transação
        try:
            db.session.bulk_save_objects(novos_enderecos)
            db.session.commit()
            print(f"{len(novos_enderecos)} endereços atualizados")
            logger.add_log(
                mensagem=f"{len(novos_enderecos)} endereços atualizados",
                tipo_log="SUCCESS",
                consulta_id=consulta_id,
                data_log=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            db.session.rollback()
            print(f"Erro de integridade ao salvar endereços: {e}")
            logger.add_log(
                mensagem=f"Erro de integridade ao salvar endereços: {e}",
                tipo_log="ERROR",
                consulta_id=consulta_id,
                data_log=datetime.now(timezone.utc)
            )

    @staticmethod
    def commit_telefone(entidade_id, consulta_id, logger, tipo_entidade_id, telefones):
        if not telefones:
            return

        # Apaga os telefones antigos de uma só vez
        Telefone.query.filter_by(entidade_id=entidade_id, tipo_entidade_id=tipo_entidade_id).delete()
        print(f"Telefones deletados para entidade_id={entidade_id}, tipo_entidade_id={tipo_entidade_id}")
        logger.add_log(
            mensagem=f"Telefones deletados para entidade_id={entidade_id}, tipo_entidade_id={tipo_entidade_id}",
            tipo_log="INFO",
            consulta_id=consulta_id,
            data_log=datetime.now(timezone.utc)
        )

        # Armazena novos telefones para inserção em lote
        novos_telefones = []
        for telefone_id, telefone in enumerate(telefones, start=1):
            novos_telefones.append(Telefone(
                telefone_id=telefone_id,
                entidade_id=entidade_id,
                tipo_entidade_id=tipo_entidade_id,
                telefone=telefone.get('telefoneComDDD', None),
                operadora=telefone.get('operadora', None),
                tipo_telefone=telefone.get('tipoTelefone', None),
                whatsapp=telefone.get('whatsApp', None)
            ))

        # Adiciona e comita em uma única transação
        try:
            db.session.bulk_save_objects(novos_telefones)
            db.session.commit()
            print(f"{len(novos_telefones)} telefones atualizados")
            logger.add_log(
                mensagem=f"{len(novos_telefones)} telefones atualizados",
                tipo_log="SUCCESS",
                consulta_id=consulta_id,
                data_log=datetime.now(timezone.utc)
            )
        except Exception as ie:
            db.session.rollback()
            print(f"Erro de integridade ao salvar telefones: {ie}")
            logger.add_log(
                mensagem=f"Erro de integridade ao salvar telefones: {ie}",
                tipo_log="ERROR",
                consulta_id=consulta_id,
                data_log=datetime.now(timezone.utc)
            )

    @staticmethod
    def commit_email(entidade_id, consulta_id, logger, tipo_entidade_id, emails):
        if not emails:
            return

        # Apaga os emails antigos de uma só vez
        Email.query.filter_by(entidade_id=entidade_id, tipo_entidade_id=tipo_entidade_id).delete()
        print(f"Emails deletados para entidade_id={entidade_id}, tipo_entidade_id={tipo_entidade_id}")
        logger.add_log(
            mensagem=f"Emails deletados para entidade_id={entidade_id}, tipo_entidade_id={tipo_entidade_id}",
            tipo_log="INFO",
            consulta_id=consulta_id,
            data_log=datetime.now(timezone.utc)
        )

        # Armazena novos emails para inserção em lote
        novos_emails = []
        for email_id, email in enumerate(emails, start=1):
            novos_emails.append(Email(
                email_id=email_id,
                entidade_id=entidade_id,
                tipo_entidade_id=tipo_entidade_id,
                email=email.get('enderecoEmail', None)
            ))

        # Adiciona e comita em uma única transação
        try:
            db.session.bulk_save_objects(novos_emails)
            db.session.commit()
            print(f"{len(novos_emails)} emails atualizados")
            logger.add_log(
                mensagem=f"{len(novos_emails)} emails atualizados",
                tipo_log="SUCCESS",
                consulta_id=consulta_id,
                data_log=datetime.now(timezone.utc)
            )
        except Exception as ie:
            db.session.rollback()
            print(f"Erro de integridade ao salvar emails: {ie}")
            logger.add_log(
                mensagem=f"Erro de integridade ao salvar emails: {ie}",
                tipo_log="ERROR",
                consulta_id=consulta_id,
                data_log=datetime.now(timezone.utc)
            )
