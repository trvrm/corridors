const MainScreen = Ractive.extend({
  css:`
  @media screen and (max-width: 768px) {
  .section {
    padding:0;
  }
}
  `,
  template:`
    <NavBar readyState={{readyState}} user={{user}}/>
    
    <section class="section">
        <div class="container">
            <Notifications notifications={{notifications}} /> 
            <div class="columns">
                <div class="column is-one-third">
                    <GameList games={{games}} ws={{ws}}/>
                </div>
                <div class="column">
                    <h1 class="title is-5">
                        Current Game is
                    </h1>
                    {{#if user.game}}
                        {{user.game.players.red.name}} - {{user.game.players.blue.name}}
                        <br>
                        <div class="has-text-centered">
                        <GameBoard game={{user.game}} ws={{ws}}/>
                        </div>
                    {{/if}}
                    
                </div>
            </div>
            
        </div>
    </section>
    
  `,
  
  oninit() {
    const protocol = (location.protocol==="http:") ? 'ws' : 'wss';
    const url      = `${protocol}://${location.host}/ws/app/`;
    const ws       = new ReconnectingWebSocket(url, null, {debug: true, reconnectInterval: 3000});
    this.set('ws',ws);
    const stateChange = () => {
        this.set('readyState', ws.readyState);
    };

    // might tighten this up even more
    // maybe [name, arg1, arg2]
    // e.g. ['set',path, value]
    // or   ['push',path,value]
    const handlers= {
        set:(keypath,value)=>{
            this.set(keypath,value);
        },
        push:(keypath,value)=>{
            this.push(keypath,value);
        }
    };
                
    ws.onmessage = event=> {
        const input = JSON.parse(event.data);
        const name = input[0];
        const args = input.slice(1);
        if (name in handlers)
            return handlers[name](...args);
        else
            console.warn(input);
    };
    
    ws.onopen       = stateChange;
    ws.onclose      = stateChange;
    ws.onerror      = stateChange;
    ws.onconnecting = stateChange;
    stateChange();
  }
});