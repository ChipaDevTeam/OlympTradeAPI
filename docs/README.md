# OlympTrade API Documentation

Professional documentation site for the OlympTrade API with interactive features, real-time trading simulation, and comprehensive guides.

## 🚀 Live Demo

Visit the documentation site: [OlympTrade API Docs](https://your-username.github.io/OlympTradeAPI/)

## 📖 Features

- **Interactive Trading Panel**: Real-time price simulation with Chart.js integration
- **Comprehensive API Reference**: Detailed documentation for all API methods
- **Practical Examples**: Working code samples for common trading scenarios
- **Modern UI/UX**: Purple-themed design with smooth animations
- **Mobile Responsive**: Optimized for all device sizes
- **Advanced Animations**: GSAP-powered effects and interactions
- **Professional Service Integration**: Direct links to bot development services

## 🛠️ Local Development

To run the documentation site locally:

1. Clone the repository:
```bash
git clone https://github.com/your-username/OlympTradeAPI.git
cd OlympTradeAPI
```

2. Navigate to the docs directory:
```bash
cd docs
```

3. Serve the files using a local web server:
```bash
# Using Python 3
python -m http.server 8000

# Using Python 2
python -m SimpleHTTPServer 8000

# Using Node.js (if you have http-server installed)
npx http-server

# Using PHP
php -S localhost:8000
```

4. Open your browser and visit `http://localhost:8000`

## 📁 Project Structure

```
docs/
├── index.html              # Main homepage
├── getting-started.html    # Installation & setup guide
├── api-reference.html      # Complete API documentation
├── examples.html           # Code examples & use cases
├── css/
│   └── style.css          # Complete styling with purple theme
├── js/
│   ├── main.js            # Main functionality
│   ├── trading-panel.js   # Interactive trading simulation
│   ├── animations.js      # GSAP animations & effects
│   └── docs.js           # Documentation-specific features
└── README.md             # This file
```

## 🎨 Customization

### Changing the Theme

The purple theme can be customized by modifying the CSS custom properties in `css/style.css`:

```css
:root {
    --primary-color: #8B5CF6;     /* Main purple */
    --primary-dark: #7C3AED;      /* Darker purple */
    --primary-light: #A78BFA;     /* Lighter purple */
    /* ... other color variables */
}
```

### Adding New Examples

To add new code examples to the Examples page:

1. Open `examples.html`
2. Create a new section with the class `example-section`
3. Add your code within a `example-card` div
4. Update the sidebar navigation in `docs.js`

### Modifying the Trading Panel

The interactive trading panel can be customized in `js/trading-panel.js`:

- Add new assets to the `assets` array
- Modify price generation in the `generatePrice()` function
- Customize chart settings in the Chart.js configuration

## 🔧 GitHub Pages Setup

This documentation is designed to work seamlessly with GitHub Pages:

1. Push your code to a GitHub repository
2. Go to your repository settings
3. Scroll down to "Pages" section
4. Select "Deploy from a branch"
5. Choose "main" branch and "/docs" folder
6. Your site will be available at `https://your-username.github.io/repository-name/`

## 📱 Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge
- Mobile browsers (iOS Safari, Chrome Mobile)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Professional Services

Need custom trading bots or advanced implementations? Visit [Chipa.tech Shop](https://chipa.tech/shop/) for professional development services.

## 📞 Support

For questions about the API or documentation:

- Create an issue in this repository
- Visit our professional services page for custom development
- Check the examples section for common use cases

---

Built with ❤️ for the trading community
