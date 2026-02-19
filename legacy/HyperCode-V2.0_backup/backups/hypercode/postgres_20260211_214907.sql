--
-- PostgreSQL database dump
--

\restrict n1JnPp17XTxQKqahf8yuxrTspQD1zWEcOhTfB0RVQ7yj3fdR51aI0fhi5SDGX4e

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
-- Name: Agent; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public."Agent" OWNER TO postgres;

--
-- Name: AuditLog; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public."AuditLog" OWNER TO postgres;

--
-- Name: Memory; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public."Memory" OWNER TO postgres;

--
-- Name: Mission; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public."Mission" OWNER TO postgres;

--
-- Name: TokenUsage; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public."TokenUsage" OWNER TO postgres;

--
-- Name: User; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."User" (
    id text NOT NULL,
    email text NOT NULL,
    name text,
    role text DEFAULT 'user'::text NOT NULL,
    "createdAt" timestamp(3) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) without time zone NOT NULL
);


ALTER TABLE public."User" OWNER TO postgres;

--
-- Data for Name: Agent; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."Agent" (id, name, role, version, capabilities, topics, "healthUrl", status, "lastHeartbeat", "createdAt", "updatedAt", "dedupKey") FROM stdin;
bdabded5-7835-40ff-b04f-512b57acdfdc	qa-engineer	qa engineer	1.0.0	{"test automation",playwright,pytest,"e2e testing","quality assurance"}	{agent.events}	http://qa-engineer:8005/health	offline	2026-02-10 03:52:00.409	2026-02-09 23:44:53.223	2026-02-11 15:53:29.687	qa-engineer
1935d908-139c-44d8-aa51-4eaaf4119971	database-architect	database architect	1.0.0	{postgresql,"schema design","query optimization",migrations,indexing}	{agent.events}	http://database-architect:8004/health	offline	2026-02-10 03:52:00.463	2026-02-09 23:44:51.996	2026-02-11 15:53:29.709	database-architect
d659509a-979d-47e6-84f4-8e65fc8dddb4	backend-specialist	backend specialist	1.0.0	{fastapi,python,"rest apis","business logic",authentication}	{agent.events}	http://backend-specialist:8003/health	offline	2026-02-10 03:52:24.637	2026-02-09 23:44:52.032	2026-02-11 15:53:29.723	backend-specialist
cd332ea4-b056-4673-9e32-dc5254df4ae4	project-strategist	project strategist	1.0.0	{"task planning",delegation,"project management",coordination}	{agent.events}	http://project-strategist:8001/health	offline	2026-02-10 03:52:25.393	2026-02-09 23:44:52.705	2026-02-11 15:53:29.735	project-strategist
c0ae1464-dec5-414d-84a2-9ef9292fbf3b	security-engineer	security engineer	1.0.0	{"security auditing",owasp,"vulnerability scanning","secure coding",compliance}	{agent.events}	http://security-engineer:8007/health	offline	2026-02-10 03:52:26.085	2026-02-09 23:44:53.037	2026-02-11 15:53:29.746	security-engineer
f2b6b828-458b-46c9-989f-249249d600f8	frontend-specialist	frontend specialist	1.0.0	{react,next.js,typescript,"tailwind css",ui/ux}	{agent.events}	http://frontend-specialist:8002/health	offline	2026-02-10 03:52:26.447	2026-02-09 23:44:52.524	2026-02-11 15:53:29.759	frontend-specialist
1fc88a89-69f8-4c76-8541-b248857ce18c	system-architect	system architect	1.0.0	{"system design","architecture patterns",scalability,"api design","technical strategy"}	{agent.events}	http://system-architect:8008/health	offline	2026-02-10 03:51:58.359	2026-02-09 23:44:52.437	2026-02-11 15:53:29.77	system-architect
747f662d-c7d4-4916-a40e-4466fb6c7bb8	devops-engineer	devops engineer	1.0.0	{docker,kubernetes,ci/cd,"infrastructure as code",monitoring}	{agent.events}	http://devops-engineer:8006/health	offline	2026-02-10 03:51:59.867	2026-02-09 23:44:52.563	2026-02-11 15:53:29.779	devops-engineer
\.


--
-- Data for Name: AuditLog; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."AuditLog" (id, "missionId", transition, "previousState", "newState", actor, "timestamp", reason, diff) FROM stdin;
\.


--
-- Data for Name: Memory; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."Memory" (id, content, type, "userId", "sessionId", metadata, keywords, "missionId", "createdAt", "updatedAt", "expiresAt") FROM stdin;
\.


--
-- Data for Name: Mission; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."Mission" (id, title, status, "agentId", "userId", "createdAt", "updatedAt", "completedAt", "retryCount", "maxRetries", payload, metadata) FROM stdin;
\.


--
-- Data for Name: TokenUsage; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."TokenUsage" (id, "missionId", model, "promptTokens", "completionTokens", "totalTokens", cost, "createdAt") FROM stdin;
\.


--
-- Data for Name: User; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."User" (id, email, name, role, "createdAt", "updatedAt") FROM stdin;
\.


--
-- Name: Agent Agent_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Agent"
    ADD CONSTRAINT "Agent_pkey" PRIMARY KEY (id);


--
-- Name: AuditLog AuditLog_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."AuditLog"
    ADD CONSTRAINT "AuditLog_pkey" PRIMARY KEY (id);


--
-- Name: Memory Memory_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Memory"
    ADD CONSTRAINT "Memory_pkey" PRIMARY KEY (id);


--
-- Name: Mission Mission_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Mission"
    ADD CONSTRAINT "Mission_pkey" PRIMARY KEY (id);


--
-- Name: TokenUsage TokenUsage_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."TokenUsage"
    ADD CONSTRAINT "TokenUsage_pkey" PRIMARY KEY (id);


--
-- Name: User User_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."User"
    ADD CONSTRAINT "User_pkey" PRIMARY KEY (id);


--
-- Name: Agent_dedupKey_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX "Agent_dedupKey_key" ON public."Agent" USING btree ("dedupKey");


--
-- Name: Agent_role_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "Agent_role_idx" ON public."Agent" USING btree (role);


--
-- Name: Agent_status_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "Agent_status_idx" ON public."Agent" USING btree (status);


--
-- Name: AuditLog_missionId_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "AuditLog_missionId_idx" ON public."AuditLog" USING btree ("missionId");


--
-- Name: Memory_sessionId_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "Memory_sessionId_idx" ON public."Memory" USING btree ("sessionId");


--
-- Name: Memory_type_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "Memory_type_idx" ON public."Memory" USING btree (type);


--
-- Name: Memory_userId_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "Memory_userId_idx" ON public."Memory" USING btree ("userId");


--
-- Name: Mission_agentId_status_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "Mission_agentId_status_idx" ON public."Mission" USING btree ("agentId", status);


--
-- Name: Mission_status_createdAt_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "Mission_status_createdAt_idx" ON public."Mission" USING btree (status, "createdAt");


--
-- Name: User_email_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX "User_email_key" ON public."User" USING btree (email);


--
-- Name: AuditLog AuditLog_missionId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."AuditLog"
    ADD CONSTRAINT "AuditLog_missionId_fkey" FOREIGN KEY ("missionId") REFERENCES public."Mission"(id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: Memory Memory_missionId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Memory"
    ADD CONSTRAINT "Memory_missionId_fkey" FOREIGN KEY ("missionId") REFERENCES public."Mission"(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: Mission Mission_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Mission"
    ADD CONSTRAINT "Mission_userId_fkey" FOREIGN KEY ("userId") REFERENCES public."User"(id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: TokenUsage TokenUsage_missionId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."TokenUsage"
    ADD CONSTRAINT "TokenUsage_missionId_fkey" FOREIGN KEY ("missionId") REFERENCES public."Mission"(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--

\unrestrict n1JnPp17XTxQKqahf8yuxrTspQD1zWEcOhTfB0RVQ7yj3fdR51aI0fhi5SDGX4e

