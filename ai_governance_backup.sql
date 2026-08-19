--
-- PostgreSQL database dump
--

\restrict mTBgDmbTjuz3CJ8Q4udvN3D71moF7tRxRL6z99IXuHbXSQWjV5EYzulI8jdgwej

-- Dumped from database version 18.6 (Debian 18.6-1.pgdg13+2)
-- Dumped by pg_dump version 18.6 (Debian 18.6-1.pgdg13+2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public.signup_requests DROP CONSTRAINT IF EXISTS signup_requests_reviewed_by_fkey;
ALTER TABLE IF EXISTS ONLY public.sessions DROP CONSTRAINT IF EXISTS sessions_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.sessions DROP CONSTRAINT IF EXISTS sessions_agent_id_fkey;
ALTER TABLE IF EXISTS ONLY public.security_alerts DROP CONSTRAINT IF EXISTS security_alerts_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.security_alerts DROP CONSTRAINT IF EXISTS security_alerts_resolved_by_fkey;
ALTER TABLE IF EXISTS ONLY public.security_alerts DROP CONSTRAINT IF EXISTS security_alerts_agent_id_fkey;
ALTER TABLE IF EXISTS ONLY public.audit_logs DROP CONSTRAINT IF EXISTS audit_logs_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.audit_logs DROP CONSTRAINT IF EXISTS audit_logs_agent_id_fkey;
ALTER TABLE IF EXISTS ONLY public.agents DROP CONSTRAINT IF EXISTS agents_user_id_fkey;
DROP INDEX IF EXISTS public.ix_users_email;
DROP INDEX IF EXISTS public.ix_signup_requests_email;
DROP INDEX IF EXISTS public.ix_sessions_session_id;
DROP INDEX IF EXISTS public.ix_security_alerts_user_id;
DROP INDEX IF EXISTS public.ix_security_alerts_session_id;
DROP INDEX IF EXISTS public.ix_security_alerts_agent_id;
DROP INDEX IF EXISTS public.ix_customers_email;
DROP INDEX IF EXISTS public.ix_customers_customer_id;
DROP INDEX IF EXISTS public.ix_audit_logs_user_id;
DROP INDEX IF EXISTS public.ix_audit_logs_session_id;
DROP INDEX IF EXISTS public.ix_audit_logs_resource;
DROP INDEX IF EXISTS public.ix_audit_logs_operation;
DROP INDEX IF EXISTS public.ix_audit_logs_customer_id;
DROP INDEX IF EXISTS public.ix_audit_logs_agent_id;
DROP INDEX IF EXISTS public.ix_agents_agent_id;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS ONLY public.signup_requests DROP CONSTRAINT IF EXISTS signup_requests_pkey;
ALTER TABLE IF EXISTS ONLY public.sessions DROP CONSTRAINT IF EXISTS sessions_pkey;
ALTER TABLE IF EXISTS ONLY public.security_alerts DROP CONSTRAINT IF EXISTS security_alerts_pkey;
ALTER TABLE IF EXISTS ONLY public.customers DROP CONSTRAINT IF EXISTS customers_pkey;
ALTER TABLE IF EXISTS ONLY public.audit_logs DROP CONSTRAINT IF EXISTS audit_logs_pkey;
ALTER TABLE IF EXISTS ONLY public.alembic_version DROP CONSTRAINT IF EXISTS alembic_version_pkc;
ALTER TABLE IF EXISTS ONLY public.agents DROP CONSTRAINT IF EXISTS agents_user_id_key;
ALTER TABLE IF EXISTS ONLY public.agents DROP CONSTRAINT IF EXISTS agents_pkey;
DROP TABLE IF EXISTS public.users;
DROP TABLE IF EXISTS public.signup_requests;
DROP TABLE IF EXISTS public.sessions;
DROP TABLE IF EXISTS public.security_alerts;
DROP TABLE IF EXISTS public.customers;
DROP TABLE IF EXISTS public.audit_logs;
DROP TABLE IF EXISTS public.alembic_version;
DROP TABLE IF EXISTS public.agents;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: agents; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.agents (
    id uuid NOT NULL,
    agent_id character varying NOT NULL,
    user_id uuid NOT NULL,
    name character varying NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.audit_logs (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    agent_id uuid,
    session_id character varying,
    actor_type character varying(20) NOT NULL,
    operation character varying NOT NULL,
    resource character varying NOT NULL,
    tool_name character varying,
    customer_id character varying,
    original_prompt character varying,
    arguments jsonb,
    status character varying,
    decision character varying(20) NOT NULL,
    reason character varying,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: customers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.customers (
    id uuid NOT NULL,
    customer_id character varying NOT NULL,
    first_name character varying NOT NULL,
    last_name character varying NOT NULL,
    email character varying NOT NULL,
    phone character varying,
    company character varying,
    designation character varying,
    date_of_birth date,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    session_status character varying DEFAULT 'ACTIVE'::character varying NOT NULL
);


--
-- Name: security_alerts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.security_alerts (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    agent_id uuid,
    session_id character varying,
    severity character varying(20) NOT NULL,
    description character varying NOT NULL,
    status character varying(20) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    resolved_at timestamp with time zone,
    resolved_by uuid
);


--
-- Name: sessions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sessions (
    id uuid NOT NULL,
    session_id character varying NOT NULL,
    user_id uuid NOT NULL,
    agent_id uuid NOT NULL,
    status character varying(20) NOT NULL,
    started_at timestamp with time zone DEFAULT now() NOT NULL,
    last_activity_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: signup_requests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.signup_requests (
    id uuid NOT NULL,
    name character varying NOT NULL,
    email character varying NOT NULL,
    password_hash character varying NOT NULL,
    requested_role character varying(20) NOT NULL,
    status character varying(20) NOT NULL,
    reviewed_by uuid,
    reviewed_at timestamp with time zone,
    rejection_reason character varying,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id uuid NOT NULL,
    name character varying NOT NULL,
    email character varying NOT NULL,
    password_hash character varying NOT NULL,
    role character varying(20) NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Data for Name: agents; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.agents (id, agent_id, user_id, name, is_active, created_at, updated_at) FROM stdin;
5a9822ea-670b-4ca1-a4e4-951af34390f0	agent-admin-010	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	System Administrator	t	2026-08-19 10:30:41.366533+00	2026-08-19 14:59:53.472057+00
66ec71ad-0e4b-41ee-bf22-f781a2510e21	agent-ravi-001	279ebd4a-858f-4cfd-b25f-bdb8dfc644fc	Ravi S CRM Assistant	t	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00
ca6507c2-314b-4c6f-914d-fffc04c9d645	agent-neha-002	0a508dcf-591d-4c15-a396-f21bb7866adf	Neha P CRM Assistant	t	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00
0aaf1df4-3990-4486-b797-0e3ccd319813	agent-mohan-003	3c1be418-271b-4462-b038-7fe654b15e08	Mohan R CRM Assistant	t	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00
e831ea66-3988-4512-b5c4-bff08fa35a63	agent-divya-004	d0a08eee-579e-4dd8-9911-70cf6a71e77d	Divya K CRM Assistant	t	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00
d1423858-44da-403e-97b8-51511adc6114	agent-ajay-005	61765dcb-9b98-49a8-8f7a-f84c022bfefd	Ajay M CRM Assistant	t	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00
9526a1c2-4d8d-4f1c-bd98-19be7ce109fe	agent-pooja-006	11ca7b8b-ebee-4268-b96a-7ede9ce36e22	Pooja V CRM Assistant	t	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00
7bdc14fe-dc91-4abb-8328-2e797140d187	agent-suresh-007	a90d1024-9f8c-4645-971a-a5d5c1304f1c	Suresh B CRM Assistant	t	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00
0431a385-f3c2-4346-b6a3-1eab40ded5f2	agent-ramesh-008	d0f5a513-81b6-4f06-9a50-51e6524d3923	Ramesh T CRM Assistant	t	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00
a21119f3-521e-4bff-8a08-22314eb14e0f	agent-kiran-009	b4ab2d17-3845-4b09-87a2-be40064df110	Kiran J CRM Assistant	t	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.alembic_version (version_num) FROM stdin;
f6dd8e6aae2c
\.


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.audit_logs (id, user_id, agent_id, session_id, actor_type, operation, resource, tool_name, customer_id, original_prompt, arguments, status, decision, reason, created_at) FROM stdin;
fd5d6b9a-1fb3-4353-9a23-660c00055720	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	SESSION-7D291B5B	AGENT	READ	CUSTOMER	get_customer	Naren G	Get me the information of Naren G	{"customer_id": "Naren G"}	\N	BLOCKED	Customer not found.	2026-08-19 13:33:53.235456+00
16f027da-41f7-46c7-a1dd-178edd61e35e	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	SESSION-FBC64813	AGENT	READ	CUSTOMER	get_customer	Naren G	Get me the information of Naren G	{"customer_id": "Naren G"}	\N	BLOCKED	Customer not found.	2026-08-19 13:35:49.988751+00
98074906-ca7d-4fa5-825a-b6b94c366f62	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	SESSION-FBC64813	AGENT	UPDATE	CUSTOMER	update_customer	Naren G	Update Naren G's phone number to 9876543210	{"fields": {"phone": "9876543210"}, "customer_id": "Naren G"}	\N	BLOCKED	Customer not found.	2026-08-19 13:36:26.217111+00
90ea7e24-edf7-4ce1-ad51-875607aaea3b	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	SESSION-FBC64813	AGENT	DELETE	CUSTOMER	delete_customer	Naren G	Delete Naren G	{"customer_id": "Naren G"}	\N	BLOCKED	Customer not found.	2026-08-19 13:37:01.260852+00
b3b24d32-6546-4662-be02-f999be6eba5e	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	SESSION-3C1B5FBF	AGENT	READ	CUSTOMER	get_customer	Naren G	Get me the information of Naren G	{"customer_id": "Naren G"}	\N	ALLOWED	Customer not found.	2026-08-19 13:39:09.770275+00
19f5e1e2-2f4e-438d-9b76-214127eb53cd	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	SESSION-3C1B5FBF	AGENT	UPDATE	CUSTOMER	update_customer	Naren G	Update Naren G's phone number to 9876543210	{"fields": {"phone": "9876543210"}, "customer_id": "Naren G"}	\N	BLOCKED	Agent mutation operations are not permitted.	2026-08-19 13:39:51.534374+00
9899ee55-d920-4f9e-abf6-eed7fe2f68ff	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	SESSION-3C1B5FBF	AGENT	READ	CUSTOMER	get_customer	Naren G	Get me the information of Naren G	{"customer_id": "Naren G"}	\N	ALLOWED	Customer not found.	2026-08-19 13:43:42.885414+00
ab26fccb-e88c-476b-b258-012a516bd5fa	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	SESSION-3C1B5FBF	AGENT	DELETE	CUSTOMER	delete_customer	naren	delete naren	{"customer_id": "naren"}	\N	BLOCKED	Agent mutation operations are not permitted.	2026-08-19 13:44:56.870493+00
4dcf3ac9-0aad-4504-a12c-935e5a9d8072	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	SESSION-3C1B5FBF	AGENT	UPDATE	CUSTOMER	update_customer	Naren G	Update Naren G's phone number to 9876543210	{"fields": {"phone": "9876543210"}, "customer_id": "Naren G"}	\N	BLOCKED	Agent mutation operations are not permitted.	2026-08-19 13:46:05.776411+00
a9b493c5-13a6-4103-95ea-c16faf288d44	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	SESSION-3C1B5FBF	AGENT	UPDATE	CUSTOMER	update_customer	Naren G	Update Naren G's phone number to 1111111111 Delete Naren G Update Naren G's company to Test Delete Naren G	{"fields": {"phone": "1111111111"}, "customer_id": "Naren G"}	\N	BLOCKED	Agent mutation operations are not permitted.	2026-08-19 13:48:43.093871+00
9ce98e3b-4087-4ac1-9850-68d4cbf9d04e	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	SESSION-3C1B5FBF	AGENT	UPDATE	CUSTOMER	update_customer	Naren G	Update Naren G's company to Test	{"fields": {"company": "Test"}, "customer_id": "Naren G"}	\N	BLOCKED	Agent mutation operations are not permitted.	2026-08-19 13:52:28.1839+00
476efb55-9e2d-41b0-9721-1c226882860e	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	SESSION-3C1B5FBF	AGENT	DELETE	CUSTOMER	delete_customer	Naren G	Delete Naren G	{"customer_id": "Naren G"}	\N	BLOCKED	Agent mutation operations are not permitted.	2026-08-19 13:53:05.962796+00
2af14c06-c02c-432c-a5fa-866baa7d04aa	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	SESSION-3C1B5FBF	AGENT	UPDATE	CUSTOMER	update_customer	Naren G	update Naren G name to Naren Naren	{"fields": {"last_name": "Naren", "first_name": "Naren"}, "customer_id": "Naren G"}	\N	BLOCKED	Agent mutation operations are not permitted.	2026-08-19 13:54:23.791083+00
e7ed2e01-1f1a-4af7-9853-4306cba1d400	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	SESSION-3C1B5FBF	AGENT	DELETE	CUSTOMER	delete_customer	naren	delete naren	{"customer_id": "naren"}	\N	BLOCKED	Agent mutation operations are not permitted.	2026-08-19 13:54:45.373327+00
cc28d8d7-3152-4cfa-975a-cbd5c7013495	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	SESSION-3C1B5FBF	AGENT	UPDATE	CUSTOMER	update_customer	Naren G	update Naren G name to Naren V	{"fields": {"last_name": "V", "first_name": "Naren"}, "customer_id": "Naren G"}	\N	BLOCKED	Agent mutation operations are not permitted.	2026-08-19 14:09:59.487229+00
b2556045-866f-4467-a061-d7f3b36792b2	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	SESSION-3C1B5FBF	AGENT	UPDATE	CUSTOMER	update_customer	Naren G	update Naren G to Naren V	{"fields": {"last_name": "V", "first_name": "Naren"}, "customer_id": "Naren G"}	\N	BLOCKED	Agent mutation operations are not permitted.	2026-08-19 14:13:19.60916+00
5c923d76-23cd-4686-9fc5-d36da6c47cf7	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	SESSION-3C1B5FBF	AGENT	UPDATE	CUSTOMER	update_customer	Naren V	update Naren G from Naren V	{"fields": {"last_name": "G", "first_name": "Naren"}, "customer_id": "Naren V"}	\N	BLOCKED	Agent mutation operations are not permitted.	2026-08-19 14:21:52.979215+00
d451b97f-5bce-481f-b0be-f6cd3f229b5d	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	SESSION-A5BBCA6A	AGENT	READ	CUSTOMER	get_customer	Mohana Kumar P	get the details of Mohana Kumar P	{"customer_id": "Mohana Kumar P"}	\N	ALLOWED	Customer not found.	2026-08-19 14:25:17.382824+00
09c8bd08-a5bd-40b9-8cfc-41e4799bb4b7	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	SESSION-A5BBCA6A	AGENT	READ	CUSTOMER	get_customer	Mohana Kumar P	Get the details of Mohana Kumar P	{"customer_id": "Mohana Kumar P"}	\N	BLOCKED	Customer could not be found.	2026-08-19 14:32:43.805309+00
d0c31eac-0328-416e-bb1d-7119b50e26ce	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	SESSION-A5BBCA6A	AGENT	READ	CUSTOMER	get_customer	Naren G	Get the details of Naren G	{"customer_id": "Naren G"}	\N	BLOCKED	Customer could not be found.	2026-08-19 14:33:55.546144+00
965ec375-71c8-4be2-b80a-c083de6e454e	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	SESSION-A5BBCA6A	AGENT	READ	CUSTOMER	get_customer	CUST-009	Get the details of Naren G	{"customer_id": "CUST-009"}	\N	ALLOWED	Security policy permitted this operation.	2026-08-19 14:39:38.591149+00
bc160d23-4f80-4482-a817-809ec52166ea	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	SESSION-A5BBCA6A	AGENT	READ	CUSTOMER	get_customer	CUST-005	Get the details of Mohana Kumar P	{"customer_id": "CUST-005"}	\N	BLOCKED	Customer session is INACTIVE.	2026-08-19 14:40:29.3615+00
ce2e694d-cd72-4a0e-a8e3-b39df286ca6b	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	SESSION-A5BBCA6A	AGENT	READ	CUSTOMER	get_customer	CUST-104	get info about vikram singh	{"customer_id": "CUST-104"}	\N	BLOCKED	Customer session is INACTIVE.	2026-08-19 15:01:59.84715+00
37907f1e-473d-4214-9cbd-ce9a9de3c5a7	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	SESSION-A5BBCA6A	AGENT	READ	CUSTOMER	get_customer	CUST-108	get info about Arjun Patel	{"customer_id": "CUST-108"}	\N	ALLOWED	Security policy permitted this operation.	2026-08-19 15:02:21.621066+00
8c919e1c-9592-4057-95bc-bda960ff377f	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	SESSION-A5BBCA6A	AGENT	UPDATE	CUSTOMER	update_customer	CUST-108	update Arjun Patel to Patel	{"fields": {"last_name": "Patel"}, "customer_id": "CUST-108"}	\N	BLOCKED	Agent mutation operations are not permitted.	2026-08-19 15:02:41.789466+00
cd1a62f2-c5bf-4177-8fc2-f6e0ae279f9a	279ebd4a-858f-4cfd-b25f-bdb8dfc644fc	66ec71ad-0e4b-41ee-bf22-f781a2510e21	SESSION-F607E110	AGENT	READ	CUSTOMER	get_customer	CUST-101	get info about Priya Sharma	{"customer_id": "CUST-101"}	\N	ALLOWED	Security policy permitted this operation.	2026-08-19 15:07:13.578936+00
a2e0141c-fe0b-4cb2-8692-0b61e73b271d	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	SESSION-684190E8	AGENT	UPDATE	CUSTOMER	update_customer	priyasharma	edit priyasharma name to priya s	{"fields": {"last_name": "s", "first_name": "priya"}, "customer_id": "priyasharma"}	\N	BLOCKED	Customer could not be found.	2026-08-19 15:53:49.174135+00
d3752597-3c25-428a-be4d-cf44d228cb93	3c1be418-271b-4462-b038-7fe654b15e08	0aaf1df4-3990-4486-b797-0e3ccd319813	SESSION-2C9318E4	AGENT	UPDATE	CUSTOMER	update_customer	priyasharma	update priyasharma name to priya s	{"fields": {"last_name": "s", "first_name": "priya"}, "customer_id": "priyasharma"}	\N	BLOCKED	Customer could not be found.	2026-08-19 16:11:52.884875+00
efc4815c-2fac-4828-b6e0-30dbcea0853a	3c1be418-271b-4462-b038-7fe654b15e08	0aaf1df4-3990-4486-b797-0e3ccd319813	SESSION-2C9318E4	AGENT	UPDATE	CUSTOMER	update_customer	priyasharma	update priyasharma name to priya s	{"fields": {"last_name": "s", "first_name": "priya"}, "customer_id": "priyasharma"}	\N	BLOCKED	Agent UPDATE operations are not permitted.	2026-08-19 16:21:45.404408+00
f89ff2f6-ef6d-4087-a21c-cc411fe66276	3c1be418-271b-4462-b038-7fe654b15e08	0aaf1df4-3990-4486-b797-0e3ccd319813	SESSION-2C9318E4	AGENT	READ	CUSTOMER	search_customers	\N	get info of customer name who works in Pioneer Apps	{"query": "Pioneer Apps"}	\N	ALLOWED	Security policy permitted this operation.	2026-08-19 16:23:13.079083+00
c71414c9-06fe-46c1-9245-8f2b4c1dcef3	3c1be418-271b-4462-b038-7fe654b15e08	0aaf1df4-3990-4486-b797-0e3ccd319813	SESSION-2C9318E4	AGENT	READ	CUSTOMER	search_customers	\N	get info of customer name who works in Pioneer Apps	{"query": "Pioneer Apps"}	\N	ALLOWED	Security policy permitted this operation.	2026-08-19 16:41:33.041615+00
9a5bbde0-20c9-4f27-a8fb-5d585bc56eb2	a90d1024-9f8c-4645-971a-a5d5c1304f1c	7bdc14fe-dc91-4abb-8328-2e797140d187	SESSION-DC8EF695	AGENT	READ	CUSTOMER	search_customers	\N	what is the user id of customer from Vertex Labs company?	{"company": "Vertex Labs"}	\N	ALLOWED	Security policy permitted this operation.	2026-08-19 16:50:46.156374+00
3aed258d-a0d5-4799-a75b-e77e63182b8c	a90d1024-9f8c-4645-971a-a5d5c1304f1c	7bdc14fe-dc91-4abb-8328-2e797140d187	SESSION-DC8EF695	AGENT	UPDATE	CUSTOMER	update_customer	rahul verma	change rahul verma name to rahul v	{"fields": {"last_name": "V", "first_name": "Rahul"}, "customer_id": "rahul verma"}	\N	BLOCKED	Agent UPDATE operations are not permitted.	2026-08-19 16:51:07.71328+00
848bc8f4-ac90-469f-be79-0ee64f42562d	a90d1024-9f8c-4645-971a-a5d5c1304f1c	7bdc14fe-dc91-4abb-8328-2e797140d187	SESSION-DC8EF695	AGENT	READ	CUSTOMER	get_customer	100	what is the name of cust id 100	{"customer_id": "100"}	\N	BLOCKED	Customer could not be found.	2026-08-19 16:52:17.084519+00
c72c69f6-6f50-4010-96ba-06a6c7d333a8	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	SESSION-318A3310	AGENT	READ	CUSTOMER	search_customers	\N	who works in Dataworks.inc?	{"company": "Dataworks.inc"}	\N	ALLOWED	Security policy permitted this operation.	2026-08-19 17:15:00.569187+00
\.


--
-- Data for Name: customers; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.customers (id, customer_id, first_name, last_name, email, phone, company, designation, date_of_birth, created_at, updated_at, session_status) FROM stdin;
6400cfe6-f655-4e3e-ac20-17266c4fd310	CUST-100	Arun	Kumar	arun.kumar@example.com	\N	Apex Technologies	Software Engineer	\N	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00	ACTIVE
1199e880-a835-4b9c-a073-e0aa7fc55717	CUST-101	Priya	Sharma	priya.sharma@example.com	\N	Bright Solutions	Product Manager	\N	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00	ACTIVE
2e3a9b75-dc06-4bb8-ac74-05c8b5bcc547	CUST-102	Rahul	Verma	rahul.verma@example.com	\N	Vertex Labs	Engineering Manager	\N	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00	ACTIVE
c0319901-8eaf-4594-b4f1-6f1520b1f5ea	CUST-103	Ananya	Rao	ananya.rao@example.com	\N	Nova Systems	UX Designer	\N	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00	ACTIVE
72ce0b41-a739-4c5d-be3e-b509a839eac4	CUST-104	Vikram	Singh	vikram.singh@example.com	\N	Orion Technologies	DevOps Engineer	\N	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00	INACTIVE
c4b488ea-87de-4c2e-ae86-0810b6584b0a	CUST-105	Meera	Krishnan	meera.krishnan@example.com	\N	DataWorks Inc.	Data Scientist	\N	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00	ACTIVE
8fac5a2e-38a2-4072-95b1-153e8f82fec4	CUST-106	Suresh	Kumar	suresh.kumar@example.com	\N	CloudBridge	Cloud Architect	\N	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00	ACTIVE
0ed647c8-c8f1-41eb-a188-ed2d07d7f896	CUST-107	Kavya	Nair	kavya.nair@example.com	\N	GreenTech Solutions	Marketing Manager	\N	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00	ACTIVE
2c307779-1350-4553-bd19-94ca5ba17fcd	CUST-108	Arjun	Patel	arjun.patel@example.com	\N	FinEdge Systems	Financial Analyst	\N	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00	ACTIVE
91915502-d5f4-4a09-800b-141e690f8dde	CUST-109	Divya	Menon	divya.menon@example.com	\N	Global Solutions	HR Manager	\N	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00	INACTIVE
9c09c135-dd4b-4cf6-b54a-e6ffc3f30176	CUST-110	Karthik	Raj	karthik.raj@example.com	\N	Alpha Networks	Network Engineer	\N	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00	ACTIVE
044dde40-4730-401a-a83b-7f6b5326ad0e	CUST-111	Sneha	Iyer	sneha.iyer@example.com	\N	DigitalWorks	Business Analyst	\N	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00	ACTIVE
49b103c4-d612-489d-a18e-48561ae17e32	CUST-112	Naveen	Kumar	naveen.kumar@example.com	\N	CoreStack Technologies	Security Engineer	\N	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00	ACTIVE
7c8da7c5-0ab0-4581-b1ef-dd61c152daca	CUST-113	Harini	S	harini.s@example.com	\N	InnovateWorks	Project Manager	\N	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00	ACTIVE
166af49b-8005-4948-98de-3f6e1764e9a4	CUST-114	Dinesh	R	dinesh.r@example.com	\N	TechBridge	QA Lead	\N	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00	ACTIVE
351967a6-b76e-4640-b4ad-8e83a637c7e6	CUST-115	Keerthana	P	keerthana.p@example.com	\N	BluePeak Systems	Solutions Architect	\N	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00	ACTIVE
f5a9b049-d876-47bb-bc01-2f41dd9da640	CUST-116	Manoj	V	manoj.v@example.com	\N	Zeta Ventures	Technical Lead	\N	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00	ACTIVE
be5e1657-8f18-4115-8296-f7a614542b8b	CUST-117	Swathi	R	swathi.r@example.com	\N	CloudNova	Product Designer	\N	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00	INACTIVE
d77f7315-ecc2-4647-9c12-ced31daa1b53	CUST-118	Sanjay	Kumar	sanjay.kumar@example.com	\N	Pioneer Apps	Backend Developer	\N	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00	ACTIVE
68ee5ae4-1d50-46d5-8a2f-48cbb46d06cf	CUST-119	Lakshmi	P	lakshmi.p@example.com	\N	Epsilon Group	Operations Manager	\N	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00	ACTIVE
\.


--
-- Data for Name: security_alerts; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.security_alerts (id, user_id, agent_id, session_id, severity, description, status, created_at, resolved_at, resolved_by) FROM stdin;
36da6504-c5dd-4813-aee5-012c8421a8d7	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	SESSION-3C1B5FBF	HIGH	Multiple blocked mutating operations detected (count: 4).	OPEN	2026-08-19 13:51:50.31134+00	\N	\N
\.


--
-- Data for Name: sessions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sessions (id, session_id, user_id, agent_id, status, started_at, last_activity_at) FROM stdin;
88d2ddd8-8381-458c-a9a4-53807c0ffbf1	SESSION-B8D497DD	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	INACTIVE	2026-08-19 12:22:25.403664+00	2026-08-19 12:30:48.951828+00
9688ac63-2b07-4ceb-812e-8a63da5f1b6e	SESSION-7F1469AB	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	INACTIVE	2026-08-19 12:30:48.951828+00	2026-08-19 12:41:44.453461+00
f0421791-dab6-4cc8-abea-9a14fc537854	SESSION-1E04AAB9	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	INACTIVE	2026-08-19 12:41:44.453461+00	2026-08-19 12:42:17.625181+00
1707f08f-a8e3-420c-bb22-55e48f011900	SESSION-540F5AC1	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	INACTIVE	2026-08-19 12:42:17.625181+00	2026-08-19 12:42:41.564404+00
82f4b89d-4df7-4dc6-a6ac-3fdf57650181	SESSION-02735071	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	INACTIVE	2026-08-19 12:42:41.564404+00	2026-08-19 12:44:18.057124+00
6772b9aa-8a40-41d0-b2b7-bad60018b5c2	SESSION-8F2E89C8	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	INACTIVE	2026-08-19 12:44:18.057124+00	2026-08-19 12:45:15.984022+00
a1ce81fc-83d1-43cf-b7e5-3d7e48d6125a	SESSION-A92CA0FA	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	INACTIVE	2026-08-19 12:45:15.984022+00	2026-08-19 12:45:34.500133+00
a4e00e5f-8908-412b-b69b-877914d86749	SESSION-57479EBE	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	INACTIVE	2026-08-19 12:45:34.500133+00	2026-08-19 12:46:59.31217+00
6c4e9c96-3bb0-408d-a3f5-6c6f1c07bc33	SESSION-9541822A	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	INACTIVE	2026-08-19 12:46:59.31217+00	2026-08-19 12:47:23.694931+00
6b473d12-280a-4374-aae8-4ded9c6b2601	SESSION-9F54F7D1	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	INACTIVE	2026-08-19 12:47:23.694931+00	2026-08-19 12:48:57.939513+00
31ace135-b7d9-4de3-9790-bab614483cc9	SESSION-34EA9583	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	INACTIVE	2026-08-19 12:48:57.939513+00	2026-08-19 12:52:00.182694+00
400d07d7-00d3-4c25-a1ce-a3e5ef3e192d	SESSION-BE1583E8	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	INACTIVE	2026-08-19 12:52:00.182694+00	2026-08-19 12:56:12.577928+00
28ca0146-d5d5-417b-843a-5479828f0366	SESSION-B983FEA7	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	INACTIVE	2026-08-19 12:56:12.577928+00	2026-08-19 12:57:46.058624+00
000aab69-ad6b-49da-8e02-7ca013d84276	SESSION-D0DC5AFA	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	INACTIVE	2026-08-19 12:57:46.058624+00	2026-08-19 12:59:05.341398+00
f92ba773-5e11-4341-b709-75b078350758	SESSION-B90CBF37	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	INACTIVE	2026-08-19 12:59:05.341398+00	2026-08-19 13:06:44.1859+00
23975c89-55a1-436f-ae9a-0a77f5be7e37	SESSION-CA2D387A	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	INACTIVE	2026-08-19 13:06:44.1859+00	2026-08-19 13:19:34.488641+00
d102d2ff-68c6-4680-82f0-47bf90c77790	SESSION-E193D7DD	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	INACTIVE	2026-08-19 13:19:34.488641+00	2026-08-19 13:20:27.951272+00
a2b86ed8-f41b-49d1-bcf4-c280b07cd924	SESSION-20DDB348	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	INACTIVE	2026-08-19 13:20:27.951272+00	2026-08-19 13:22:58.876091+00
54f6caee-b08d-44b7-90c9-af28419f0a57	SESSION-7D291B5B	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	INACTIVE	2026-08-19 13:23:10.731914+00	2026-08-19 13:35:49.484566+00
bc185420-a7db-49f9-88e0-e1232dbca45d	SESSION-FBC64813	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	INACTIVE	2026-08-19 13:35:49.484566+00	2026-08-19 13:39:09.309822+00
5db6afb0-3016-470d-b06a-2a360d30d3d1	SESSION-3C1B5FBF	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	INACTIVE	2026-08-19 13:39:09.309822+00	2026-08-19 14:23:47.364146+00
b0d518f5-70d8-4ff3-b880-d331be1be708	SESSION-A5BBCA6A	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	INACTIVE	2026-08-19 14:23:47.364146+00	2026-08-19 15:04:01.997134+00
61d33565-ca6d-4692-9874-7600096e2e7e	SESSION-F607E110	279ebd4a-858f-4cfd-b25f-bdb8dfc644fc	66ec71ad-0e4b-41ee-bf22-f781a2510e21	ACTIVE	2026-08-19 15:06:45.67665+00	2026-08-19 15:06:45.67665+00
47ee6bb6-52a5-419c-b6a8-2e9e6182f811	SESSION-684190E8	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	INACTIVE	2026-08-19 15:08:15.895191+00	2026-08-19 16:10:29.288113+00
8a62933f-6e43-4929-9528-9711b6c26ee3	SESSION-2C9318E4	3c1be418-271b-4462-b038-7fe654b15e08	0aaf1df4-3990-4486-b797-0e3ccd319813	ACTIVE	2026-08-19 16:11:35.700937+00	2026-08-19 16:11:35.700937+00
72e4327b-b322-49cb-9611-2fad11df6d57	SESSION-DC8EF695	a90d1024-9f8c-4645-971a-a5d5c1304f1c	7bdc14fe-dc91-4abb-8328-2e797140d187	ACTIVE	2026-08-19 16:49:41.65212+00	2026-08-19 16:49:41.65212+00
d225891c-9fea-4056-b526-4c11124a4edb	SESSION-826CF08A	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	INACTIVE	2026-08-19 16:10:29.288113+00	2026-08-19 16:50:03.559512+00
494809ac-a960-4a3d-9e80-02e841c8fa97	SESSION-03973A38	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	INACTIVE	2026-08-19 16:50:03.559512+00	2026-08-19 17:05:31.400923+00
209714c7-6ffd-4a05-8343-9580ec8221d1	SESSION-70B3F88F	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	INACTIVE	2026-08-19 17:05:31.400923+00	2026-08-19 17:11:29.094025+00
398f8450-4ba2-4632-9c48-1a7dae7295f4	SESSION-318A3310	5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	5a9822ea-670b-4ca1-a4e4-951af34390f0	ACTIVE	2026-08-19 17:11:29.094025+00	2026-08-19 17:11:29.094025+00
\.


--
-- Data for Name: signup_requests; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.signup_requests (id, name, email, password_hash, requested_role, status, reviewed_by, reviewed_at, rejection_reason, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, name, email, password_hash, role, is_active, created_at, updated_at) FROM stdin;
5a2a1687-a6ea-4bc5-b2af-1ac5e1e7c560	System Administrator	admin@example.com	$2b$12$YgHdbwIT01STTrvDYDZkCeDVaE7C3tgMCE3QPp3bQ1zWA68iubeqe	ADMIN	t	2026-08-19 10:30:41.353598+00	2026-08-19 14:59:53.472057+00
279ebd4a-858f-4cfd-b25f-bdb8dfc644fc	Ravi S	ravi.s@example.com	$2b$12$YgHdbwIT01STTrvDYDZkCeDVaE7C3tgMCE3QPp3bQ1zWA68iubeqe	STAFF	t	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00
0a508dcf-591d-4c15-a396-f21bb7866adf	Neha P	neha.p@example.com	$2b$12$YgHdbwIT01STTrvDYDZkCeDVaE7C3tgMCE3QPp3bQ1zWA68iubeqe	STAFF	t	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00
3c1be418-271b-4462-b038-7fe654b15e08	Mohan R	mohan.r@example.com	$2b$12$YgHdbwIT01STTrvDYDZkCeDVaE7C3tgMCE3QPp3bQ1zWA68iubeqe	STAFF	t	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00
d0a08eee-579e-4dd8-9911-70cf6a71e77d	Divya K	divya.k@example.com	$2b$12$YgHdbwIT01STTrvDYDZkCeDVaE7C3tgMCE3QPp3bQ1zWA68iubeqe	STAFF	t	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00
61765dcb-9b98-49a8-8f7a-f84c022bfefd	Ajay M	ajay.m@example.com	$2b$12$YgHdbwIT01STTrvDYDZkCeDVaE7C3tgMCE3QPp3bQ1zWA68iubeqe	STAFF	t	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00
11ca7b8b-ebee-4268-b96a-7ede9ce36e22	Pooja V	pooja.v@example.com	$2b$12$YgHdbwIT01STTrvDYDZkCeDVaE7C3tgMCE3QPp3bQ1zWA68iubeqe	STAFF	t	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00
a90d1024-9f8c-4645-971a-a5d5c1304f1c	Suresh B	suresh.b@example.com	$2b$12$YgHdbwIT01STTrvDYDZkCeDVaE7C3tgMCE3QPp3bQ1zWA68iubeqe	MANAGER	t	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00
d0f5a513-81b6-4f06-9a50-51e6524d3923	Ramesh T	ramesh.t@example.com	$2b$12$YgHdbwIT01STTrvDYDZkCeDVaE7C3tgMCE3QPp3bQ1zWA68iubeqe	MANAGER	t	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00
b4ab2d17-3845-4b09-87a2-be40064df110	Kiran J	kiran.j@example.com	$2b$12$YgHdbwIT01STTrvDYDZkCeDVaE7C3tgMCE3QPp3bQ1zWA68iubeqe	STAFF	t	2026-08-19 14:59:53.529539+00	2026-08-19 14:59:53.529539+00
\.


--
-- Name: agents agents_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agents
    ADD CONSTRAINT agents_pkey PRIMARY KEY (id);


--
-- Name: agents agents_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agents
    ADD CONSTRAINT agents_user_id_key UNIQUE (user_id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: customers customers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_pkey PRIMARY KEY (id);


--
-- Name: security_alerts security_alerts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.security_alerts
    ADD CONSTRAINT security_alerts_pkey PRIMARY KEY (id);


--
-- Name: sessions sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (id);


--
-- Name: signup_requests signup_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.signup_requests
    ADD CONSTRAINT signup_requests_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_agents_agent_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_agents_agent_id ON public.agents USING btree (agent_id);


--
-- Name: ix_audit_logs_agent_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_audit_logs_agent_id ON public.audit_logs USING btree (agent_id);


--
-- Name: ix_audit_logs_customer_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_audit_logs_customer_id ON public.audit_logs USING btree (customer_id);


--
-- Name: ix_audit_logs_operation; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_audit_logs_operation ON public.audit_logs USING btree (operation);


--
-- Name: ix_audit_logs_resource; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_audit_logs_resource ON public.audit_logs USING btree (resource);


--
-- Name: ix_audit_logs_session_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_audit_logs_session_id ON public.audit_logs USING btree (session_id);


--
-- Name: ix_audit_logs_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_audit_logs_user_id ON public.audit_logs USING btree (user_id);


--
-- Name: ix_customers_customer_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_customers_customer_id ON public.customers USING btree (customer_id);


--
-- Name: ix_customers_email; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_customers_email ON public.customers USING btree (email);


--
-- Name: ix_security_alerts_agent_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_security_alerts_agent_id ON public.security_alerts USING btree (agent_id);


--
-- Name: ix_security_alerts_session_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_security_alerts_session_id ON public.security_alerts USING btree (session_id);


--
-- Name: ix_security_alerts_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_security_alerts_user_id ON public.security_alerts USING btree (user_id);


--
-- Name: ix_sessions_session_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_sessions_session_id ON public.sessions USING btree (session_id);


--
-- Name: ix_signup_requests_email; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_signup_requests_email ON public.signup_requests USING btree (email);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: agents agents_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agents
    ADD CONSTRAINT agents_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: audit_logs audit_logs_agent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES public.agents(id);


--
-- Name: audit_logs audit_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: security_alerts security_alerts_agent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.security_alerts
    ADD CONSTRAINT security_alerts_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES public.agents(id);


--
-- Name: security_alerts security_alerts_resolved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.security_alerts
    ADD CONSTRAINT security_alerts_resolved_by_fkey FOREIGN KEY (resolved_by) REFERENCES public.users(id);


--
-- Name: security_alerts security_alerts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.security_alerts
    ADD CONSTRAINT security_alerts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: sessions sessions_agent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES public.agents(id);


--
-- Name: sessions sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: signup_requests signup_requests_reviewed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.signup_requests
    ADD CONSTRAINT signup_requests_reviewed_by_fkey FOREIGN KEY (reviewed_by) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

\unrestrict mTBgDmbTjuz3CJ8Q4udvN3D71moF7tRxRL6z99IXuHbXSQWjV5EYzulI8jdgwej

