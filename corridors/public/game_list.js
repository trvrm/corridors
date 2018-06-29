
Ractive.components.GameList = Ractive.extend({
        
    template:`
    <h1 class="title is-4">Available Games:</h1>
    <table class="table">
        <thead>
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
    
        
    <button 
      class="button is-info"
        on-click="ws.send('new_game')"
      >
      New game
  </button>
`
});
    