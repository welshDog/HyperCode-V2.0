--
-- PostgreSQL database dump
--

\restrict ZMfr3L1HIlJ31Qg2Q91goKvNV9hQcFBmahSO8iuTYv0UBInosObfMiyAg6uelJi

-- Dumped from database version 15.15
-- Dumped by pg_dump version 15.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: Agent; Type: TABLE; Schema: public; Owner: hyper
--

CREATE TABLE public."Agent" (
    id text NOT NULL,
    name text NOT NULL,
    role text NOT NULL,
    version text NOT NULL,
    capabilities text[],
    topics text[],
    "healthUrl" text,
    status text DEFAULT 'offline'::text NOT NULL,
    "lastHeartbeat" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL,
    "dedupKey" text
);


ALTER TABLE public."Agent" OWNER TO hyper;

--
-- Name: AuditLog; Type: TABLE; Schema: public; Owner: hyper
--

CREATE TABLE public."AuditLog" (
    id text NOT NULL,
    "missionId" text NOT NULL,
    transition text NOT NULL,
    "previousState" text NOT NULL,
    "newState" text NOT NULL,
    actor text NOT NULL,
    "timestamp" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    reason text,
    diff jsonb
);


ALTER TABLE public."AuditLog" OWNER TO hyper;

--
-- Name: Memory; Type: TABLE; Schema: public; Owner: hyper
--

CREATE TABLE public."Memory" (
    id text NOT NULL,
    content text NOT NULL,
    type text NOT NULL,
    "userId" text,
    "sessionId" text,
    metadata jsonb,
    keywords text[],
    "missionId" text,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL,
    "expiresAt" timestamp(3) without time zone
);


ALTER TABLE public."Memory" OWNER TO hyper;

--
-- Name: Mission; Type: TABLE; Schema: public; Owner: hyper
--

CREATE TABLE public."Mission" (
    id text NOT NULL,
    title text NOT NULL,
    status text DEFAULT 'pending'::text NOT NULL,
    "agentId" text,
    "userId" text NOT NULL,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL,
    "completedAt" timestamp(3) without time zone,
    "retryCount" integer DEFAULT 0 NOT NULL,
    "maxRetries" integer DEFAULT 3 NOT NULL,
    payload jsonb,
    metadata jsonb
);


ALTER TABLE public."Mission" OWNER TO hyper;

--
-- Name: TokenUsage; Type: TABLE; Schema: public; Owner: hyper
--

CREATE TABLE public."TokenUsage" (
    id text NOT NULL,
    "missionId" text,
    model text NOT NULL,
    "promptTokens" integer NOT NULL,
    "completionTokens" integer NOT NULL,
    "totalTokens" integer NOT NULL,
    cost double precision NOT NULL,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public."TokenUsage" OWNER TO hyper;

--
-- Name: User; Type: TABLE; Schema: public; Owner: hyper
--

CREATE TABLE public."User" (
    id text NOT NULL,
    email text NOT NULL,
    name text,
    role text DEFAULT 'user'::text NOT NULL,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL
);


ALTER TABLE public."User" OWNER TO hyper;

--
-- Data for Name: Agent; Type: TABLE DATA; Schema: public; Owner: hyper
--

COPY public."Agent" (id, name, role, version, capabilities, topics, "healthUrl", status, "lastHeartbeat", "createdAt", "updatedAt", "dedupKey") FROM stdin;
\.


--
-- Data for Name: AuditLog; Type: TABLE DATA; Schema: public; Owner: hyper
--

COPY public."AuditLog" (id, "missionId", transition, "previousState", "newState", actor, "timestamp", reason, diff) FROM stdin;
\.


--
-- Data for Name: Memory; Type: TABLE DATA; Schema: public; Owner: hyper
--

COPY public."Memory" (id, content, type, "userId", "sessionId", metadata, keywords, "missionId", "createdAt", "updatedAt", "expiresAt") FROM stdin;
\.


--
-- Data for Name: Mission; Type: TABLE DATA; Schema: public; Owner: hyper
--

COPY public."Mission" (id, title, status, "agentId", "userId", "createdAt", "updatedAt", "completedAt", "retryCount", "maxRetries", payload, metadata) FROM stdin;
\.


--
-- Data for Name: TokenUsage; Type: TABLE DATA; Schema: public; Owner: hyper
--

COPY public."TokenUsage" (id, "missionId", model, "promptTokens", "completionTokens", "totalTokens", cost, "createdAt") FROM stdin;
\.


--
-- Data for Name: User; Type: TABLE DATA; Schema: public; Owner: hyper
--

COPY public."User" (id, email, name, role, "createdAt", "updatedAt") FROM stdin;
\.


--
-- Name: Agent Agent_pkey; Type: CONSTRAINT; Schema: public; Owner: hyper
--

ALTER TABLE ONLY public."Agent"
    ADD CONSTRAINT "Agent_pkey" PRIMARY KEY (id);


--
-- Name: AuditLog AuditLog_pkey; Type: CONSTRAINT; Schema: public; Owner: hyper
--

ALTER TABLE ONLY public."AuditLog"
    ADD CONSTRAINT "AuditLog_pkey" PRIMARY KEY (id);


--
-- Name: Memory Memory_pkey; Type: CONSTRAINT; Schema: public; Owner: hyper
--

ALTER TABLE ONLY public."Memory"
    ADD CONSTRAINT "Memory_pkey" PRIMARY KEY (id);


--
-- Name: Mission Mission_pkey; Type: CONSTRAINT; Schema: public; Owner: hyper
--

ALTER TABLE ONLY public."Mission"
    ADD CONSTRAINT "Mission_pkey" PRIMARY KEY (id);


--
-- Name: TokenUsage TokenUsage_pkey; Type: CONSTRAINT; Schema: public; Owner: hyper
--

ALTER TABLE ONLY public."TokenUsage"
    ADD CONSTRAINT "TokenUsage_pkey" PRIMARY KEY (id);


--
-- Name: User User_pkey; Type: CONSTRAINT; Schema: public; Owner: hyper
--

ALTER TABLE ONLY public."User"
    ADD CONSTRAINT "User_pkey" PRIMARY KEY (id);


--
-- Name: Agent_dedupKey_key; Type: INDEX; Schema: public; Owner: hyper
--

CREATE UNIQUE INDEX "Agent_dedupKey_key" ON public."Agent" USING btree ("dedupKey");


--
-- Name: Agent_role_idx; Type: INDEX; Schema: public; Owner: hyper
--

CREATE INDEX "Agent_role_idx" ON public."Agent" USING btree (role);


--
-- Name: Agent_status_idx; Type: INDEX; Schema: public; Owner: hyper
--

CREATE INDEX "Agent_status_idx" ON public."Agent" USING btree (status);


--
-- Name: AuditLog_missionId_idx; Type: INDEX; Schema: public; Owner: hyper
--

CREATE INDEX "AuditLog_missionId_idx" ON public."AuditLog" USING btree ("missionId");


--
-- Name: Memory_sessionId_idx; Type: INDEX; Schema: public; Owner: hyper
--

CREATE INDEX "Memory_sessionId_idx" ON public."Memory" USING btree ("sessionId");


--
-- Name: Memory_type_idx; Type: INDEX; Schema: public; Owner: hyper
--

CREATE INDEX "Memory_type_idx" ON public."Memory" USING btree (type);


--
-- Name: Memory_userId_idx; Type: INDEX; Schema: public; Owner: hyper
--

CREATE INDEX "Memory_userId_idx" ON public."Memory" USING btree ("userId");


--
-- Name: Mission_agentId_status_idx; Type: INDEX; Schema: public; Owner: hyper
--

CREATE INDEX "Mission_agentId_status_idx" ON public."Mission" USING btree ("agentId", status);


--
-- Name: Mission_status_createdAt_idx; Type: INDEX; Schema: public; Owner: hyper
--

CREATE INDEX "Mission_status_createdAt_idx" ON public."Mission" USING btree (status, "createdAt");


--
-- Name: User_email_key; Type: INDEX; Schema: public; Owner: hyper
--

CREATE UNIQUE INDEX "User_email_key" ON public."User" USING btree (email);


--
-- Name: AuditLog AuditLog_missionId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: hyper
--

ALTER TABLE ONLY public."AuditLog"
    ADD CONSTRAINT "AuditLog_missionId_fkey" FOREIGN KEY ("missionId") REFERENCES public."Mission"(id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: Memory Memory_missionId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: hyper
--

ALTER TABLE ONLY public."Memory"
    ADD CONSTRAINT "Memory_missionId_fkey" FOREIGN KEY ("missionId") REFERENCES public."Mission"(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: Mission Mission_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: hyper
--

ALTER TABLE ONLY public."Mission"
    ADD CONSTRAINT "Mission_userId_fkey" FOREIGN KEY ("userId") REFERENCES public."User"(id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: TokenUsage TokenUsage_missionId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: hyper
--

ALTER TABLE ONLY public."TokenUsage"
    ADD CONSTRAINT "TokenUsage_missionId_fkey" FOREIGN KEY ("missionId") REFERENCES public."Mission"(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--

\unrestrict ZMfr3L1HIlJ31Qg2Q91goKvNV9hQcFBmahSO8iuTYv0UBInosObfMiyAg6uelJi

