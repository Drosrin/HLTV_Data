def visualize_player_stats(stats:dict[str, str]) -> str:
    return \
    f"""
    
    ======== Player Stat Report ========
    Rating: {stats['rt']}   T Side Rating: {stats['t_side_rt']}   CT Side Rating: {stats['ct_side_rt']}
    Round Swing: {stats['round_swing']}   DPR(Death Per Round): {stats['dpr']} KAST(Kill, Assist, Survived or Traded): {stats['kast']}
    Multi-Kill: {stats['multi_kill']}   ADR(Average Damage Per Round): {stats['adr']}   KPR(Kill Per Round): {stats['kpr']}
    ====================================
    """