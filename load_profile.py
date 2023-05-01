import pstats

stats = pstats.Stats("profile.stats")
stats.sort_stats(pstats.SortKey.CUMULATIVE).print_stats()
