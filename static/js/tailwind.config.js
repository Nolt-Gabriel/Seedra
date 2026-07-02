
    tailwind.config = {

      content: [
        "./templates/**/*.html"
      ],
      theme: {
        extend: {
          fontFamily: {
            sans: ['Balsamiq Sans', 'sans-serif'],
            lato: ['Lato', 'sans-serif']
          },
          colors: {
            seedra: {
              leafDark: '#044b2d',
              leafMid: '#587e49',
              leafLight: '#78b863',
              seedBrown: '#9a774c',
              seedSand: '#ddd1ae',
              seedMist: '#d9d6cc',
              deepForest: '#001500',
              stone: '#888784',
              cloud: '#d9d9d9'
            }
          },
          boxShadow: {
            soft: '0 10px 30px rgba(4,75,45,0.10)',
            card: '0 8px 24px rgba(0,21,0,0.08)'
          },
          backgroundImage: {
            organic: 'radial-gradient(circle at top right, rgba(120,184,99,0.18), transparent 28%), radial-gradient(circle at bottom left, rgba(154,119,76,0.16), transparent 30%)'
          }
        }
      }
    }
  