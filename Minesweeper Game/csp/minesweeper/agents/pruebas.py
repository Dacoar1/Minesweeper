
ancho=3
alto=5

def tile_to_var(x: int, y: int, ancho) -> int:
        
        return y+ ancho*x
    
def var_to_tile( var: int,ancho):
        return ( var // ancho,var % ancho)
    
def neighbors( x: int, y: int, ancho,alto):
        """Example."""
        xy=tile_to_var(x,y,ancho)
        width, height = ancho, alto
        neighbors = []
        for dy in range(-1 if y > 0 else 0, 2 if y < height - 1 else 1):
            for dx in range(-1 if x > 0 else 0, 2 if x < width - 1 else 1):
                dxy=tile_to_var(x + dx, y + dy,ancho)
                if dxy!=xy:
                    neighbors.append((dxy))
        return neighbors
    
print(tile_to_var(3,2,ancho))
print(var_to_tile(6,ancho))

