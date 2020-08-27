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

@bot.event
async def on_ready():
    print("Logged in as {0.user}".format(bot))

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
    G = nx.Graph()
    plt.clf()
    print(nodes)
    print(edges)
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    nx.draw(G, with_labels=True)
    plt.savefig("resources/output.png")

@bot.command()
async def info(ctx, content):
    """Gets info on a user"""
    granted = ctx.message.guild.get_member_named(content)
    if granted == None:
        await ctx.channel.send("{0} is not a valid argument".format(content))
        return
    try:
        output = [ctx.message.guild.get_member(grantee).name for grantee in grants if grants[grantee] == granted.id]
    except AttributeError:
        output = []
    nodes = output
    edges = [(name, granted.name) for name in output]
    if len(output) > 0:
        await ctx.channel.send("{0} is trusted by {1}: {2}".format(granted.name, len(output), output))
    else:
        await ctx.channel.send("{0} is trusted by {1}".format(granted.name, len(output)))
    try:
        await ctx.channel.send("{0} trusts: {1}".format(granted.name, ctx.message.guild.get_member(grants[granted.id]).name))
        edges.append((granted.name, ctx.message.guild.get_member(grants[granted.id]).name))
        output.append(ctx.message.guild.get_member(grants[granted.id]).name)
    except KeyError:
        await ctx.channel.send("{0} trusts nobody".format(granted.name))
    drawNodes(nodes, edges)

    await ctx.channel.send(file=discord.File('resources/output.png'))

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