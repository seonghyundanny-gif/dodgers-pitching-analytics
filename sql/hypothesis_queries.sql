-- ============================================================
-- 가설 1 (투수 레벨): 구속↑ → IL_Days↑, WAR_per_IP/Postseason_WAR↑
-- ============================================================

-- Q1. 시즌별 평균 구속 vs 평균 IL일수 vs 평균 WAR_per_IP (구속-부상-효율 트렌드)
SELECT
    season,
    ROUND(AVG(fastball_velo_mph), 2) AS avg_fastball_velo,
    ROUND(AVG(IL_days), 1)           AS avg_IL_days,
    ROUND(AVG(WAR_per_IP), 4)        AS avg_WAR_per_IP,
    ROUND(AVG(Postseason_WAR_proxy), 2) AS avg_postseason_war_proxy
FROM pitcher_stats
WHERE low_sample_flag = 0
GROUP BY season
ORDER BY season;

-- Q2. 구속 구간(bucket)별 평균 IL일수 / WAR_per_IP 비교 (구속이 높을수록 부상↑·효율↑인지)
SELECT
    CASE
        WHEN fastball_velo_mph < 92 THEN '1) <92mph'
        WHEN fastball_velo_mph < 94 THEN '2) 92-94mph'
        WHEN fastball_velo_mph < 96 THEN '3) 94-96mph'
        ELSE '4) 96mph+'
    END AS velo_bucket,
    COUNT(*)                          AS n_pitcher_seasons,
    ROUND(AVG(IL_days), 1)            AS avg_IL_days,
    ROUND(AVG(WAR_per_IP), 4)         AS avg_WAR_per_IP,
    ROUND(AVG(Postseason_WAR_proxy), 2) AS avg_postseason_war_proxy
FROM pitcher_stats
WHERE low_sample_flag = 0
GROUP BY velo_bucket
ORDER BY velo_bucket;

-- Q3. 선수별 상관관계 확인용 원자료 (구속, IL일수, WAR_per_IP, 나이, IP를 한 줄로 — Python에서 회귀할 때 그대로 사용 가능)
SELECT
    season, name, Age, IP_decimal, fastball_velo_mph,
    IL_days, WAR_per_IP, K_pct, Postseason_WAR_proxy
FROM pitcher_stats
WHERE low_sample_flag = 0
ORDER BY season, fastball_velo_mph DESC;

-- Q4. 구속 Top10 시즌과 그 해 IL일수 (고구속 투수의 부상 리스크 사례 확인)
SELECT season, name, fastball_velo_mph, IL_days, WAR_per_IP
FROM pitcher_stats
WHERE low_sample_flag = 0
ORDER BY fastball_velo_mph DESC
LIMIT 10;


-- ============================================================
-- 가설 2 (구단 레벨): 2024년 이후(Superstar_Era) MC vs MB 비교
-- ============================================================

-- Q5. Before(2017-19,22-23) vs After(2024-25) 핵심 재정 지표 평균 비교
SELECT
    CASE WHEN Superstar_Era = 1 THEN 'After 2024' ELSE 'Before 2024' END AS era,
    COUNT(*)                                  AS n_seasons,
    ROUND(AVG(total_adjusted_payroll), 0)     AS avg_payroll,
    ROUND(AVG(CBT_Tax_Paid), 0)               AS avg_CBT_tax_paid,
    ROUND(AVG(Injured_Salary_Loss), 0)        AS avg_injured_salary_loss,
    ROUND(AVG(Road_Attendance), 0)            AS avg_road_attendance,
    ROUND(AVG(Postseason_Home_Games), 1)      AS avg_postseason_home_games
FROM team_financials
GROUP BY era;

-- Q6. 연도별 전체 한계비용(MC) 추이: CBT_Tax_Paid + Injured_Salary_Loss
SELECT
    season,
    CBT_Tax_Paid,
    Injured_Salary_Loss,
    ROUND(CBT_Tax_Paid + Injured_Salary_Loss, 0) AS total_marginal_cost,
    Superstar_Era
FROM team_financials
ORDER BY season;

-- Q7. 투수 레벨 WAR을 구단 단위로 합산해 시즌별 팀 투수진 총 WAR과 재정 지표 결합 (Part1 + Part2 join)
SELECT
    p.season,
    ROUND(SUM(p.WAR), 1)            AS team_total_pitcher_WAR,
    ROUND(SUM(p.Postseason_WAR_proxy), 2) AS team_total_postseason_war_proxy,
    t.CBT_Tax_Paid,
    t.Injured_Salary_Loss,
    t.Postseason_Home_Games
FROM pitcher_stats p
JOIN team_financials t ON p.season = t.season
GROUP BY p.season
ORDER BY p.season;
