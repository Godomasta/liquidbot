import matplotlib.pyplot as plt
import networkx as nx
import configparser
import discord
import time
import json
from discord.ext import commands

bot = commands.Bot(command_prefix="~", description="CivBot")

try:
    grants = json.load(open('resources/grants.json'))
    print(grants)
except FileNotFoundError:
    print("No grants found")
    grants = dict()
except json.decoder.JSONDecodeError:
    print("Couldn't load grants")
    grants = dict()
"""JSON stores keys as str, convert back to int"""
grants = {int(key):value for key,value in grants.items()}

@bot.event
async def on_ready():
    print("Logged in as {0.user}".format(bot))

"""Returns the ids of members that DIRECTLY trust user"""
def getPower(ctx, user):
    power = []
    for key in grants:
        if grants[key] == user:
            power.append(ctx.message.guild.get_member(key).name)
    return power

"""Returns the ids of members that DIRECTLY and INDIRECTLY trust user"""
def crawlPower(ctx, user):
    edges = []
    def crawl(user):
        for key in grants:
            if grants[key] == user:
                edges.append((ctx.message.guild.get_member(key).name, ctx.message.guild.get_member(user).name, len(crawlPower(ctx, key))+1))
                crawl(key)
    for key in grants:
        if grants[key] == user:
            edges.append((ctx.message.guild.get_member(key).name, ctx.message.guild.get_member(user).name, len(crawlPower(ctx, key))+1))
            crawl(key)
    return edges

@bot.command()
async def trust(ctx, content):
    """Trusts a user"""
    granted = ctx.message.guild.get_member_named(content)
    grantee = ctx.author
    try:
        grants[grantee.id] = granted.id
    except AttributeError:
        await ctx.channel.send("{0} is not a valid argument".format(content))
        return        
    with open("resources/grants.json", "w") as file:
        json.dump(grants, file)
    await ctx.channel.send("Granted {0}'s voting power to {1}".format(grantee.name, granted.name))
    print(grants)

def drawNodes(nodes, edges):
    G = nx.DiGraph()
    plt.clf()
    G.add_nodes_from(nodes)
    for edge in edges:
        u,v,w = edge
        G.add_edge(u, v, weight=w)
    widths = [G[u][v]['weight'] for u,v in G.edges()]
    nx.draw(G, with_labels=True, width=widths)
    plt.savefig("resources/output.png")

@bot.command()
async def info(ctx, content):
    """Gets info on a user"""
    granted = ctx.message.guild.get_member_named(content)
    if granted == None:
        await ctx.channel.send("{0} is not a valid argument".format(content))
        return
    output = getPower(ctx, granted.id)
    if len(output) > 0:
        await ctx.channel.send("{0} is trusted by {1}: {2}".format(granted.name, len(output), output))
    else:
        await ctx.channel.send("{0} is trusted by {1}".format(granted.name, len(output)))
    try:
        await ctx.channel.send("{0} trusts: {1}".format(granted.name, ctx.message.guild.get_member(grants[granted.id]).name))
    except KeyError:
        await ctx.channel.send("{0} trusts nobody".format(granted.name))

    edges = crawlPower(ctx, granted.id)
    nodes = []
    for u,v,_ in edges:
        if u not in nodes:
            nodes.append(u)
        if v not in nodes:
            nodes.append(v)
    drawNodes(nodes, edges)
    await ctx.channel.send(file=discord.File('resources/output.png'))
    await ctx.channel.send("{0} has a power of: {1}".format(granted.name, len(edges)+1))

if __name__ == "__main__":
    config_type = 'test'
    config = configparser.ConfigParser()
    config.read('config.ini')
    token = config.get(config_type, 'token')
    while True:
        try:
            bot.run(token)
        except Exception as e:
            print("Error", e)
        print("Waiting until restart")
        time.sleep(10)