ALTER SESSION SET CONTAINER=FREEPDB1;
ALTER SESSION SET CURRENT_SCHEMA=MPI_NOTIFY_USER;

GRANT ALL PRIVILEGES TO MPI_NOTIFY_USER IDENTIFIED BY "test";
GRANT UNLIMITED TABLESPACE TO MPI_NOTIFY_USER;

CREATE TABLESPACE MPI_NOTIFY_USER DATAFILE 'mpi_notify_user.dbf' SIZE 100M AUTOEXTEND ON NEXT 10M MAXSIZE UNLIMITED;

COMMIT;

CREATE TABLE notify_message_queue (
  nhs_number            VARCHAR2 (10) NOT NULL,
  event_status_id       NUMBER (38),
  batch_id              VARCHAR2 (36),
  message_id            VARCHAR2 (36),
  message_definition_id NUMBER (38) NOT NULL,
  message_status        VARCHAR2 (25) NOT NULL,
  subject_id            NUMBER (38),
  event_id              NUMBER (38),
  pio_id                NUMBER (38),
  created_datestamp     TIMESTAMP (6) DEFAULT SYSTIMESTAMP NOT NULL,
  read_datestamp        TIMESTAMP (6),
  bcss_error_id         NUMBER (38),
  address_id            NUMBER (38),
  address_version_id    NUMBER (38),
  address_line_1        VARCHAR2 (40),
  address_line_2        VARCHAR2 (40),
  address_line_3        VARCHAR2 (40),
  address_line_4        VARCHAR2 (40),
  address_line_5        VARCHAR2 (40),
  postcode              VARCHAR2 (12),
  gp_practice_name      VARCHAR2 (100)
)
RESULT_CACHE (MODE DEFAULT)
TABLESPACE MPI_NOTIFY_USER
NOCOMPRESS;

CREATE TABLE notify_message_definition (
  message_definition_id         NUMBER (38) NOT NULL,
  routing_plan_id               VARCHAR2 (36) NOT NULL,
  event_status_id               NUMBER (38) NOT NULL,
  message_code                  VARCHAR2 (12) NOT NULL,
  message_name                  VARCHAR2 (100) NOT NULL,
  parameter_id                  NUMBER (38),
  end_date                      DATE,
  audit_reason                  VARCHAR2 (250) NOT NULL,
  variable_text_1               VARCHAR2 (4000),
  prevalent_incident_status_id  NUMBER (38),
  gp_practice_endorsement       VARCHAR2 (1),
  subject_had_cancer_previously VARCHAR2 (1)
)
RESULT_CACHE (MODE DEFAULT)
TABLESPACE MPI_NOTIFY_USER
NOCOMPRESS;

CREATE TABLE message_types (
  message_type_id   NUMBER (38) NOT NULL,
  message_type_name VARCHAR2 (100) NOT NULL
)
RESULT_CACHE (MODE DEFAULT)
TABLESPACE MPI_NOTIFY_USER
NOCOMPRESS;

CREATE TABLE notify_message_batch (
  batch_id              VARCHAR2 (36) NOT NULL,
  message_definition_id	NUMBER (38) NOT NULL,
  batch_status          VARCHAR2 (25) NOT NULL
)
RESULT_CACHE (MODE DEFAULT)
TABLESPACE MPI_NOTIFY_USER
NOCOMPRESS;

CREATE TABLE ep_event_status_transition_t (
  key_id          NUMBER (38) NOT NULL,
  event_id        NUMBER (38) NOT NULL,
  from_status_id  NUMBER (38) NOT NULL,
  to_status_id    NUMBER (38) NOT NULL
)
RESULT_CACHE (MODE DEFAULT)
TABLESPACE mpi_notify_user
NOCOMPRESS;

COMMIT;

CREATE OR REPLACE PACKAGE MPI_NOTIFY_USER.pkg_notify_wrap AS
  FUNCTION f_get_next_batch (pi_batch_id IN notify_message_batch.batch_id%TYPE)
    RETURN notify_message_definition.routing_plan_id%TYPE;

  FUNCTION f_update_message_status (
    pi_batch_id         IN notify_message_queue.batch_id%TYPE,
    pi_message_id       IN notify_message_queue.message_id%TYPE,
    pi_message_status   IN notify_message_queue.message_status%TYPE
  )
    RETURN message_types.message_type_id%TYPE;

END pkg_notify_wrap;
/

CREATE OR REPLACE PACKAGE BODY MPI_NOTIFY_USER.pkg_notify_wrap AS
  FUNCTION f_get_next_batch (pi_batch_id IN notify_message_batch.batch_id%TYPE)
    RETURN notify_message_definition.routing_plan_id%TYPE IS
    v_routing_plan_id notify_message_definition.routing_plan_id%TYPE;
    c_function_name  CONSTANT VARCHAR2 (35) := 'PKG_NOTIFY.f_get_next_batch';
  BEGIN
    SELECT  nmd.routing_plan_id
    INTO    v_routing_plan_id
    FROM    notify_message_definition nmd
    WHERE   nmd.message_definition_id = 1;

    UPDATE  notify_message_queue nmq
    SET     nmq.batch_id      = pi_batch_id,
            nmq.message_status = 'requested'
    WHERE   nmq.message_status = 'new'
    AND     nmq.message_definition_id = 1;
    RETURN  v_routing_plan_id;
  END f_get_next_batch;

  FUNCTION f_update_message_status (
    pi_batch_id         IN notify_message_queue.batch_id%TYPE,
    pi_message_id       IN notify_message_queue.message_id%TYPE,
    pi_message_status   IN notify_message_queue.message_status%TYPE
  )
    RETURN message_types.message_type_id%TYPE IS
    v_error_id            message_types.message_type_id%TYPE := 0;
  BEGIN
    UPDATE  notify_message_queue nmq
    SET     nmq.message_status = pi_message_status,
            nmq.read_datestamp = SYSTIMESTAMP
    WHERE   nmq.batch_id = pi_batch_id
    AND     nmq.message_id = pi_message_id;
    RETURN  v_error_id;
  END f_update_message_status;
END pkg_notify_wrap;
/

SHOW ERRORS;

COMMIT;

CREATE OR REPLACE VIEW MPI_NOTIFY_USER.v_notify_message_queue
AS
  SELECT  nmq.nhs_number,
          nmq.message_id,
          nmq.batch_id,
          nmd.routing_plan_id,
          nmq.message_status,
          nmd.variable_text_1,
          nmq.address_line_1,
          nmq.address_line_2,
          nmq.address_line_3,
          nmq.address_line_4,
          nmq.address_line_5,
          nmq.postcode
  FROM MPI_NOTIFY_USER.notify_message_queue nmq
      INNER JOIN MPI_NOTIFY_USER.notify_message_definition nmd
         ON nmd.message_definition_id = nmq.message_definition_id;


INSERT INTO MPI_NOTIFY_USER.notify_message_definition (message_definition_id, routing_plan_id, event_status_id, message_code, message_name, parameter_id, end_date, audit_reason, prevalent_incident_status_id, gp_practice_endorsement, subject_had_cancer_previously, variable_text_1) VALUES (
1, 'c3f31ae4-1532-46df-b121-3503db6b32d6', 11197, 'S1a', 'Pre-invitation: incident subjects with no previous cancer diagnosis', 212, NULL, 'BCSS-18672', 203151, NULL, 'N', 'We offer screening every 2 years to try and find signs of bowel cancer at an early stage when there are no symptoms. This is when treatment can be more effective.');

INSERT INTO MPI_NOTIFY_USER.notify_message_definition (message_definition_id, routing_plan_id, event_status_id, message_code, message_name, parameter_id, end_date, audit_reason, prevalent_incident_status_id, gp_practice_endorsement, subject_had_cancer_previously, variable_text_1) VALUES (
2, 'c3f31ae4-1532-46df-b121-3503db6b32d6', 11197, 'S1b', 'Pre-invitation: incident subjects with previous cancer diagnosis', 212, NULL, 'BCSS-18672', 203151, NULL, 'Y', 'Routine screening may not be suitable if you are having ongoing care or treatment for a bowel condition, following a previous referral. You can contact us for advice.');


COMMIT;
