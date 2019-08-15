import pandas as pd
import utils
import matplotlib.pyplot as plt
import config

market_settings = config.market_settings



def to_df(raw_result, params):
    def flatten_cols(row):
        timestep = row['timestep']
        substep = row['substep']
        run = row['run']
        s = row['s']
        new_cols = {}
        miners = utils.get_nodes_by_type(s, 'miner')
        players = utils.get_nodes_by_type(s, 'player')
        clovers = utils.get_nodes_by_type(s, 'clover')
        sample_clover = {'hasSymmetry': True}
        for key in s['symmetries'].keys():
            if key == 'hasSymmetry': continue
            sample_clover[key] = False
        for key in s['symmetries'].keys():
            if key == 'hasSymmetry': continue
            clover = dict(sample_clover)
            clover[key] = True
            reward = utils.getCloverReward(s['symmetries'], clover, params['payMultiplier'])
            new_cols['reward-' + key] = reward
            cashout = utils.calculateCashout(s, market_settings, reward)
            if (cashout == 0):
                cashout = .001311
            new_cols['reward-eth-' + key] = cashout

        # timestep stats
        new_cols['cloversKept'] = s['timestepStats']['cloversKept']
        new_cols['cloversReleased'] = s['timestepStats']['cloversReleased']
        new_cols['cloversTraded'] = s['timestepStats']['cloversTraded']
        new_cols['cloversBoughtFromBank'] = s['timestepStats']['cloversBoughtFromBank']
        new_cols['cloversListedByPlayers'] = s['timestepStats']['cloversListedByPlayers']

        new_cols['cost-to-mine'] = market_settings['register_clover_cost_in_eth']
        new_cols['cost-to-mine-usd'] = market_settings['register_clover_cost_in_eth'] * 300
        new_cols['miners'] = len(miners)
        new_cols['players'] = len(players)
        new_cols['clovers'] = len(clovers)
        new_cols.update(s['symmetries'])
        price = utils.calculateCurrentPrice(s, market_settings)
        if (price == 0):
#             _s = raw_results[(row['timestep'] - 1) * len(partial_state_update_blocks)]
#             price = utils.calculateCurrentPrice(_s, market_settings)
            price = 0.000803
        new_cols['coin-price'] = price
        new_cols['coin-price-usd'] = new_cols['coin-price'] * 300
        # new_cols['playerClovers'] = new_cols['clovers'] = new_cols['bankClovers']
        # for clover_attr in ['hasSymmetry', 'y0Sym', 'x0Sym', 'xySym', 'xnySym', 'rotSym', 'pretty']:
        #     new_cols['net_' + clover_attr] = len([c for c in clovers if g.nodes[c][clover_attr]])

        res = {**row, **s, **new_cols}
        res.pop('network')
#         res.pop('hasSymmetry')
        res.pop('previous-timesteps')
        res.pop('symmetries')
        res.pop('bank')
#         res.pop('miners')
#         res.pop('players')
#         res.pop('clovers')
        res.pop('run')
        res.pop('s')
        return res

    df = pd.DataFrame(map(flatten_cols, raw_result))
    df = df[df['substep'] == df['substep'].max()]

    df['market-cap'] = df['coin-price'] * df['bc-totalSupply'] * 300

    return df

def graph_clovers_metrics_backup(results, graphsize=(15,8), monte_run=0, save=False):
    num_results = len(results)
    fig = plt.figure(figsize=(graphsize[0]*num_results, graphsize[1]))
    axs = fig.subplots(1, num_results)

    for (i, result) in enumerage(results):
        df.plot('timestep', ['cloversKept', 'cloversReleased', 'coin-price'], secondary_y=['coin-price'], ax=axs[i])
# utils.savefig(fig, previousRuns, timesteps_per_run, 'hrs-price-graph')

def make_graph(results, graph, graphsize=(15,8), monte_run=0, save=False, paramTitle=False):
    num_results = len(results)
    fig = plt.figure(figsize=(graphsize[0]*num_results, graphsize[1]))
    axs = fig.subplots(1, num_results)

    for (i, res) in enumerate(results):

        params = res['simulation_parameters']['M']
        df = to_df(res['result'], params)
        pText = params if paramTitle else ""

        graph(df, pText, axs) if num_results == 1 else graph(df, pText, axs[i])
# utils.savefig(fig, previousRuns, timesteps_per_run, 'hrs-price-graph')

def clovers_metrics_graph(df, params, axs):
    title = "Clovers Kept & Released vs Coin Price %s" % params
    return df.plot('timestep', ['cloversKept', 'cloversReleased', 'coin-price'], secondary_y=['coin-price'], ax=axs, title=title)


def clovers_traded_graph(df, params, axs):
    title = "Clovers Traded, Bought or Listed vs Coin Price %s" % params
    return df.plot('timestep', ['cloversTraded','cloversBoughtFromBank', 'cloversListedByPlayers', 'coin-price'], secondary_y=['coin-price'], ax=axs, title=title)

def bc_balance_graph(df, params, axs):
    title = "BC Balance vs BC Total Supply %s" % params
    return df.plot('timestep', ['bc-balance', 'bc-totalSupply'], secondary_y=['bc-totalSupply'], ax=axs, title=title)

def market_cap_graph(df, params, axs):
    title = "Market Cap vs Coin Price %s" % params
    return df.plot('timestep', ['coin-price', 'market-cap'], secondary_y=['coin-price'], ax=axs, title=title)

def num_syms_graph(df, params, axs):
    title = "Num Symmetries %s" % params
    return df.plot('timestep', ['rotSym', 'x0Sym', 'y0Sym', 'xySym', 'xnySym'], ax=axs, title=title)

def rewards_per_sym_graph(df, params, axs):
    title = "Rewards per Sym %s" % params
    return df.plot('timestep', ['reward-rotSym', 'reward-x0Sym', 'reward-y0Sym', 'reward-xySym', 'reward-xnySym'], ax=axs, title=title)


def rewards_per_sym_eth_graph(df, params, axs):
    title = "Rewards per Sym (ETH) vs Mining Cost %s" % params
    return df.plot('timestep', ['reward-eth-rotSym', 'reward-eth-x0Sym', 'reward-eth-y0Sym', 'reward-eth-xySym', 'reward-eth-xnySym', 'cost-to-mine'], ax=axs, title=title)


def make_final_state_graph(results, graphsize=(15,8)):
    num_results = len(results)
    fig = plt.figure(figsize=(graphsize[0]*num_results, 2*graphsize[1]))
    axs = fig.subplots(2, num_results)

    for (i, res) in enumerate(results):
        params = res['simulation_parameters']['M']

        final_state = res['result'][-1]['s']
        g = utils.getNetwork(params)
        miners = utils.get_nodes_by_type(final_state, 'miner')
        players = utils.get_nodes_by_type(final_state, 'player')

        cols_to_graph = ['eth-spent', 'eth-earned', 'supply']

        plot_data = [
            {
                "nodes": players,
                "title": "Final Balance (ETH & CLV) of Players %s" % params,
                "x_label": "Player",
                "axis": (axs[0] if len(results) == 1 else axs[0,i])
            },
            {
                "nodes": miners,
                "title": "Final Balance (ETH & CLV) of Miners",
                "x_label": "Miner",
                "axis": (axs[1] if num_results == 1 else axs[1,i])
            }
        ]

        for plot in plot_data:
            if (len(plot['nodes']) > 0):
                df = pd.DataFrame([g.nodes[player] for player in plot['nodes']])
                df[['eth-spent', 'eth-earned', 'supply']].plot(kind='bar', ax=plot['axis'], secondary_y='supply')
            plot['axis'].set(xlabel=plot['x_label'], ylabel='ETH', title=plot['title'])
            ax_2y = plot['axis'].twinx()
            ax_2y.set_ylabel("CloverCoin", labelpad=32)
            ax_2y.set_yticks([])
        # utils.savefig(fig, previousRuns, timesteps_per_run, 'hrs-eth-graph')
