import teamsData from "../../data/teams.json";
import teamNamesJp from "../../data/team_names_jp.json";

// チームのスラッグを取得するヘルパー
export const getTeamLink = (leagueId: string, teamName: string) => {
    if (!teamName) return null;
    const leagueKey = leagueId.startsWith('league-one') ? 'league-one' : leagueId;
    const cleanName = teamName.trim();
    
    // 1. 完全一致
    let team = (teamsData as any).find((t: any) =>
        t.league === leagueKey && t.team_name === cleanName
    );

    // 2. 旧チーム名などのエイリアス一致（改称後もスクレイピング元が旧名称を使うケース）
    if (!team) {
        team = (teamsData as any).find((t: any) =>
            t.league === leagueKey && (t.aliases || []).includes(cleanName)
        );
    }

    // 3. 部分一致 (teams.json の名称が長い場合など)
    if (!team) {
        team = (teamsData as any).find((t: any) =>
            t.league === leagueKey && (t.team_name.includes(cleanName) || cleanName.includes(t.team_name))
        );
    }
    
    return team ? `/teams/${leagueKey}/${team.slug}` : null;
};

// チーム名正規化関数
export const normalizeTeam = (leagueId: string, name: string) => {
    if (!name) return { name: "Unknown", flag: null };
    const leagueKey = leagueId.startsWith('league-one') ? 'league-one' : leagueId;
    const leagueData = (teamNamesJp as any)[leagueKey] || {};
    const cleanInput = name.trim();
    
    if (leagueData[cleanInput]) return { name: leagueData[cleanInput].jp, flag: leagueData[cleanInput].flag };
    for (const [fullName, data] of Object.entries(leagueData)) {
        if ((data as any).jp === cleanInput) return { name: (data as any).jp, flag: (data as any).flag };
    }
    
    for (const [fullName, data] of Object.entries(leagueData)) {
        const d = data as any;
        const lowerInput = cleanInput.toLowerCase();
        if (d.aliases?.some((a: string) => a.toLowerCase().trim() === lowerInput) || 
            fullName.toLowerCase().trim().includes(lowerInput) ||
            lowerInput.includes(fullName.toLowerCase().trim())) {
            return { name: d.jp, flag: d.flag };
        }
    }
    
    return { name: cleanInput, flag: null };
};

// Round ごとにグルーピング
export const groupByRound = (leagueId: string, results: any[]) => {
    const filteredResults = results.filter(r => {
        const home = r.home || "";
        const away = r.away || "";
        const garbage = ["リーグ戦", "準々", "準決", "決勝", "決定戦", "入替戦", "TBD"];
        return !garbage.some(g => home.includes(g) || away.includes(g));
    });

    const allEnhancedResults = filteredResults.map(r => {
        const normHome = normalizeTeam(leagueId, r.home);
        const normAway = normalizeTeam(leagueId, r.away);
        return {
            ...r,
            home: normHome.name,
            home_flag: normHome.flag || r.home_flag,
            home_link: getTeamLink(leagueId, normHome.name),
            away: normAway.name,
            away_flag: normAway.flag || r.away_flag,
            away_link: getTeamLink(leagueId, normAway.name),
            round: parseInt(r.round) || 0,
            _dateObj: new Date(r.date.replace(/\//g, '-'))
        };
    });

    const groups: { [key: number]: any[] } = {};
    allEnhancedResults.forEach(m => {
        const round = m.round;
        if (!groups[round]) groups[round] = [];
        groups[round].push(m);
    });

    return Object.keys(groups)
        .map(Number)
        .sort((a, b) => b - a)
        .map(round => {
            const matches = groups[round].sort((a, b) => b._dateObj.getTime() - a._dateObj.getTime());
            const dates = matches.map(m => m.date).filter(Boolean).sort();
            const minDate = dates[0] ? dates[0].replace(/-/g, '.') : "";
            const maxDate = dates[dates.length - 1] ? dates[dates.length - 1].replace(/-/g, '.') : "";
            const isAllFuture = matches.every(m => m.score === "VS" || m.score === "vs");
            
            return {
                round,
                matches,
                dateRange: minDate && maxDate ? (minDate === maxDate ? minDate : `${minDate} 〜 ${maxDate}`) : "",
                isAllFuture
            };
        });
};
