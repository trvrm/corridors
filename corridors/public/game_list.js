
Ractive.components.GameList = Ractive.extend({
    css:`
    .table.is-scrollable tbody {
      overflow-y: scroll;
      max-height:20em;
    }

    `,
    template:`
    

<button class="button is-info is-small is-outlined is-rounded" on-click="ws.send('new_game','human')">
    New game vs human
</button>

<button class="button is-info is-small is-outlined is-rounded" on-click="ws.send('new_game','bot')">
    New game vs bot
</button>

    <table class="table is-scrollable">
        <thead>
            <tr>
                <th colspan="5 ">
                    Games
                </th>
            </tr>
            <tr>
                <th></th>
                <th>Red</th>
                <th>Blue</th>
                <th>Time</th>
                <th>Turn</th>
            </tr>
        </thead>
        <tbody>
            {{#each games as game}}
                <tr>
                    <td>
                        {{#if !(game.players.blue)}}
                            <button 
                                class="button is-info is-small"
                                on-click="ws.send('join_game',game.uuid)"
                            >
                                Join
                            </button>
                        {{/if}}
                    </td>
                
                    <td>{{game.players.red.name}}</td>
                    <td>{{game.players.blue.name}}</td>
                    <td>0:00</td>
                    <td>{{game.turn}}</td>
                <tr>
            {{/each}}
        </tbody>
    </table>
    
        
`
});
    