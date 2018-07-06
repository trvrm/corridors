/*
    I want a mechanism for highlighting legal moves.
    
    This means 2 things: SENDING the legal moves with the board state.
    Painting them in response to mouse activity.
    
    Maybe we have a clickable overlay when it's your turn?
    
    
*/
Ractive.components.GameBoard = Ractive.extend({
    
    css:`
        .board{
            fill:#741b34;
        }
        
        .square.black{
            fill:#000000;
        }
        
        .highlighted{
            fill:rgba(240,240,0,0.15);
        }
        .highlighted:hover{
            fill:rgba(240,240,0,0.8);
        }
        .wall{
            fill: #eedab6;
        }
        .wallslot{
            fill: #000000;
        }.
        
        .piece{
            
        }
        .piece.selected{
            stroke:yellow;
            stroke-width:4;
        }
    `,    
 
    template:`
        <svg width="650" height="500" class=" default">
            <g class="board" transform="rotate({{current_color=='red'?0:180}} 325 250)">
                <rect width="650" height="500" class="border"></rect>
                <g class="bluewalls" transform="translate(0,15)">
                    
                    {{#each [0,1,2,3,4,5,6,7,8,9] as i}}
                        {{#if (game.board.blue.walls) && (game.board.turn==current_color) && (current_color=='blue')}}
                            <rect 
                                on-click="ws.send('game.select','wall')"
                                x="5" y="{{i*50}}" width="90" height="8"   rx="2" ry="2" 
                                class="{{i<game.board.blue.walls?'wall':'wallslot'}}"
                            ></rect>
                        {{else}}
                            <rect 
                                x="5" y="{{i*50}}" width="90" height="8"   rx="2" ry="2" 
                                class="{{i<game.board.blue.walls?'wall':'wallslot'}}"
                            >
                            </rect>
                        {{/if}}
                        
                    {{/each}}
                    
                </g>
                <g class="redwalls" transform="translate(550,15)">
                    
                    {{#each [0,1,2,3,4,5,6,7,8,9] as i}}
                        {{#if (game.board.red.walls) && (game.board.turn==current_color) && (current_color=='red')}}
                            <rect 
                                on-click="ws.send('game.select','wall')"
                                x="5" y="{{i*50}}" width="90" height="8"   rx="2" ry="2" 
                                class="{{i<game.board.red.walls?'wall':'wallslot'}}"
                            ></rect>
                        {{else}}
                            <rect 
                                x="5" y="{{i*50}}" width="90" height="8"   rx="2" ry="2" 
                                class="{{i<game.board.red.walls?'wall':'wallslot'}}"
                            ></rect>
                        {{/if}}
                    
                    {{/each}}
                </g>
                <g transform="translate(100,20) " class="squares">
                    {{#each [0,1,2,3,4,5,6,7,8] as j}}
                        {{#each [0,1,2,3,4,5,6,7,8] as i}}
                            <rect 
                                x="{{5+(i*50)}}" 
                                y="{{5+(j*50)}}" 
                                rx="3"
                                ry="3"
                                width="40" 
                                height="40" 
                                class="square black"
                                >
                            </rect>
                            
                             
                        {{/each}}
                    {{/each}}
                    {{#if game.selected=='piece'}}
                        {{#each game.locations as l:num}}
                            <rect 
                                x="{{5+(l[1]*50)}}" 
                                y="{{5+(l[0]*50)}}" 
                                rx="3"
                                ry="3"
                                width="40" 
                                height="40" 
                                class="square highlighted"
                                on-click="ws.send('game.command',game.commands[num])"
                                >
                                
                            </rect>
                        {{/each}}
                    {{/if}}
                    <g class="piece blue" transform="translate({{50*game.board.blue.location[1]}},{{50*game.board.blue.location[0]}})">
                        {{#if (game.board.turn==current_color) && (current_color=='blue')}}
                            <circle cx="25" cy="25" r="15" stroke="black" stroke-width="1" fill="blue" 
                                on-click="ws.send('game.select','piece')"
                                class="piece {{game.selected=='piece'?'selected':''}}"
                            />
                        {{else}}
                            <circle cx="25" cy="25" r="15" stroke="black" stroke-width="1" fill="blue" />
                        {{/if}}
                    </g>
                    <g class="piece red" transform="translate({{50*game.board.red.location[1]}},{{50*game.board.red.location[0]}})">
                        {{#if (game.board.turn==current_color) && (current_color=='red')}}
                            <circle cx="25" cy="25" r="15" stroke="black" stroke-width="1" fill="red" 
                                on-click="ws.send('game.select','piece')"
                                class="piece {{game.selected=='piece'?'selected':''}}"
                            />
                        {{else}}
                            <circle cx="25" cy="25" r="15" stroke="black" stroke-width="1" fill="red" />
                        {{/if}}
                        
                    </g>
                </g>
                
                <g transform="translate(150,70)" class="wall_slots">
                    {{#each game.board.walls as row:j}}
                        {{#each row as wall:i}}
                            {{#if wall==1}}
                                <g transform="translate({{i*50}},{{j*50}})">
                                    <rect x="-45" y="-3" width="90" height="8"   rx="2" ry="2" class="wall"></rect>
                                </g>
                            {{/if}}
                            {{#if wall==-1}}
                                <g transform="translate({{i*50}},{{j*50}})">
                                    <rect x="-3" y="-45" width="8" height="90"  rx="2" ry="2" class="wall">
                                    </rect>
                                </g>
                            {{/if}}
                        {{/each}}
                    {{/each}}
                    
                    {{#if game.selected=='hwall'}}
                        {{#each game.locations as l:num}}
                            <g transform="translate({{l[1]*50}},{{l[0]*50}})">
                                <rect
                                    on-click="ws.send('game.command',game.commands[num])"
                                 x="-45" y="-3" width="90" height="8"   rx="2" ry="2" class="highlighted"></rect>
                            </g>
                        {{/each}}
                    {{/if}}
                    {{#if game.selected=='vwall'}}
                        {{#each game.locations as l:num}}
                            <g transform="translate({{l[1]*50}},{{l[0]*50}})">
                                <rect 
                                    on-click="ws.send('game.command',game.commands[num])"
                                    x="-3" y="-45" width="8" height="90"   rx="2" ry="2" class="highlighted"></rect>
                            </g>
                        {{/each}}
                    {{/if}}
                
                </g>
            </g>
        </svg>

        {{#if game.over}}
            <h3>Game Over</h3>
            Winner: {{game.winner}}
        {{/if}}
        
        <pre style="display:none">
            DEBUG
            
            walls: {{game.board.red.walls}}/{{game.board[current_color].walls}}
            Current Color:{{current_color}}
            Other Color: {{other_color}}
            Your Turn2: {{game.board.turn==current_color}}
        
        
            Selected: {{game.selected}}
        
            Red: {{game.players.red.uuid}}
            Blue: {{game.players.blue.uuid}}
            Me: {{user.uuid}}
            Turn: {{game.board.turn}}
            Player: {{game.players[game.board.turn].uuid}}
            Your turn: {{game.players[game.board.turn].uuid==user.uuid}}
            Locations: 
            {{#each game.locations as l}}
                {{JSON.stringify(l)}}
            {{/each}}
            
        </pre>
        
        
    ` 
});