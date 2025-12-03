// Mock data for development
const mockProducts = [
    {
        id: 1,
        name: "Traditional Thangka Painting",
        price: 850,
        originalPrice: 1200,
        category: "artwork",
        image: "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=400&fit=crop",
        description: "Hand-painted traditional Buddhist Thangka with intricate details",
        rating: 4.8,
        reviews: 23,
        bestseller: true,
        inStock: 15
    },
    {
        id: 2,
        name: "Wooden Pagoda Model",
        price: 450,
        originalPrice: 600,
        category: "handicrafts",
        image: "https://images.unsplash.com/photo-1545558014-8692077e9b5c?w=400&h=400&fit=crop",
        description: "Miniature replica of Bhaktapur's famous Nyatapola Temple",
        rating: 4.6,
        reviews: 18,
        bestseller: true,
        inStock: 8
    },
    {
        id: 3,
        name: "Nepali Pashmina Shawl",
        price: 320,
        originalPrice: 450,
        category: "textiles",
        image: "https://images.unsplash.com/photo-1584464491033-06628f3a6b7b?w=400&h=400&fit=crop",
        description: "Premium cashmere pashmina with traditional patterns",
        rating: 4.9,
        reviews: 34,
        bestseller: false,
        inStock: 25
    },
    {
        id: 4,
        name: "Ceramic Pottery Set",
        price: 280,
        originalPrice: 380,
        category: "pottery",
        image: "https://images.unsplash.com/photo-1578749556568-bc2c40e68b61?w=400&h=400&fit=crop",
        description: "Hand-crafted ceramic bowls with traditional Newari designs",
        rating: 4.7,
        reviews: 12,
        bestseller: false,
        inStock: 20
    },
    {
        id: 5,
        name: "Silver Temple Jewelry",
        price: 650,
        originalPrice: 850,
        category: "jewelry",
        image: "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=400&h=400&fit=crop",
        description: "Traditional Nepali silver jewelry with precious stones",
        rating: 4.8,
        reviews: 29,
        bestseller: true,
        inStock: 12
    },
    {
        id: 6,
        name: "Khukuri Knife Set",
        price: 480,
        originalPrice: 650,
        category: "handicrafts",
        image: "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=400&fit=crop",
        description: "Authentic Gurkha Khukuri with decorative sheath",
        rating: 4.5,
        reviews: 16,
        bestseller: false,
        inStock: 10
    },
    {
        id: 7,
        name: "Singing Bowl Set",
        price: 380,
        originalPrice: 520,
        category: "handicrafts",
        image: "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400&h=400&fit=crop",
        description: "Hand-forged Tibetan singing bowl with wooden striker",
        rating: 4.9,
        reviews: 41,
        bestseller: true,
        inStock: 18
    },
    {
        id: 8,
        name: "Wood Carved Mask",
        price: 220,
        originalPrice: 300,
        category: "artwork",
        image: "https://images.unsplash.com/photo-1578749556568-bc2c40e68b61?w=400&h=400&fit=crop",
        description: "Traditional Bhairav mask used in cultural festivals",
        rating: 4.4,
        reviews: 8,
        bestseller: false,
        inStock: 22
    }
];

const categories = [
    { id: 'all', name: 'All Products', count: 8 },
    { id: 'artwork', name: 'Artwork', count: 2 },
    { id: 'handicrafts', name: 'Handicrafts', count: 3 },
    { id: 'textiles', name: 'Textiles', count: 1 },
    { id: 'pottery', name: 'Pottery', count: 1 },
    { id: 'jewelry', name: 'Jewelry', count: 1 }
];

const priceRanges = [
    { id: 'all', name: 'All Prices', min: 0, max: Infinity },
    { id: '0-300', name: 'Under Rs. 300', min: 0, max: 300 },
    { id: '300-500', name: 'Rs. 300 - 500', min: 300, max: 500 },
    { id: '500-700', name: 'Rs. 500 - 700', min: 500, max: 700 },
    { id: '700+', name: 'Above Rs. 700', min: 700, max: Infinity }
];

const sortOptions = [
    { id: 'featured', name: 'Featured' },
    { id: 'price-low', name: 'Price: Low to High' },
    { id: 'price-high', name: 'Price: High to Low' },
    { id: 'rating', name: 'Highest Rated' },
    { id: 'popularity', name: 'Most Popular' }
];